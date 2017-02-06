from re import split, search, M, findall
from pprint import pprint
from Tiling import Block, Tiling, PermSetTiled
from Cover import Cover
from permuta import PermSet, Perm
from permuta.misc import flatten

import os
from pymongo import MongoClient
mongo = MongoClient('mongodb://localhost:27017/')

def perm_to_one_str(perm):
    return "".join([str(1 + i) for i in list(perm)])

def avoids_to_delimited(permset, delim='_'):
    return delim.join([perm_to_one_str(perm) for perm in permset.basis])

def av_string_to_permset(av):
    avoids = findall(r'(\[(\[[0-9 ,]*\](, \[[0-9 ,]*\])*)?\])', av)
    if not avoids:
        raise ValueError("Could not find double list in string av: {s}".format(av))
    else:
        avoids = avoids[0][0]
    avoids = eval(avoids)
    return PermSet.avoiding([Perm.one(perm) for perm in avoids])


def permset_to_av_string(permset):
    """Takes the basis of the PermSet, converts the Perms to one based then into lists"""
    arr = [list([ i + 1 for i in perm ]) for perm in permset.basis]
    return 'Av({})'.format(str( arr ))


def parse_log(inp, avoids=None, file=True):
    if not file and not avoids:
        raise ValueError("When file argument is False, avoids must not be None")
    tilings = []

    if not avoids:
        avoids = findall(r'([0-9]+(_[0-9]+)*)', inp)[0][0]
        avoids = PermSet.avoiding([Perm.one([int(i) for i in list(perm)]) for perm in avoids.split("_")])

    if file:
        with open(inp) as f:
            inp = f.read()

    # Only take the last cover found
    inp = split(r'Found:\n', inp)[-1]

    # Split on 123124:\n0101010100110101010 to find all rule blocks on the form
    # +-+-+-+-+
    # | |o| | |
    # +-+-+-+-+
    # | | | |o|
    # +-+-+-+-+
    # | | |1| |
    # +-+-+-+-+
    # |o| | | |
    # +-+-+-+-+
    # 1: Av([[2, 1]])
    for i, el in enumerate(split(r'\d+:\s?\n[01]+', inp)[1:]):
        # We always take the first rule in a block, they are seperated by two newlines
        item = el.strip().split('\n\n')[0]
        table = []
        permsets = {}
        rule = {}

        # Parse each line
        for i in split('\n', item):
            if i.startswith('+'):
                continue
            if i.startswith('|'):
                table.append( i.strip().split('|')[1:-1] )
            else:
                num, avstring = i.split(': ')
                permsets[num] = av_string_to_permset(avstring)

        for i in range(len(table)):
            for j in range(len(table[i])):
                char = table[i][j]
                if char == 'X':
                    rule[(i, j)] = avoids
                elif char.isnumeric():
                    rule[(i, j)] = permsets.get(char, None)
                elif char == 'o':
                    rule[(i, j)] = Block.point
        tilings.append(Tiling(rule))
    return Cover(avoids, tilings)

def cover_to_json(cover):
    example_json_structure = {
        "_id" : 'ObjectId("5882153c7e98af0c473a874e")',
        "avoid" : "o",
        "length": 19, # Length of basis
        "rank": 4, # The rank of the Cover
        "tile" : [
            [
                {
                    "point" : [
                        0,
                        0
                    ],
                    "val" : "o"
                }
            ]
        ],
        "examples" : {
            "1" : [
                "1"
            ]
        },
        "recurrence" : {
            "0" : "0",
            "1" : "1",
            "n" : "0"
        },
        "genf" : "F(x) = x",
        "solved_genf" : "F(x) = x",
        "coeffs" : [
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
    }
    obj = {}
    tiles = []
    for tiling in cover:
        tile = []
        for k, v in tiling.items():
            point = {}
            point['point'] = [k[0],k[1]]
            if v == Block.point:
                point['val'] = 'o'
            else:
                point['val'] = permset_to_av_string(v)
            tile.append(point)
        tiles.append(tile)

    # Code that will be used later to generate examples
    # Create examples
    examples = {}
    for i in range(2, 6):
        if not str(i) in examples:
            # Set of all length i permutations
            examples[str(i)] = set()
        for T in cover:
            for perm in PermSetTiled(T).of_length(i):
                examples[str(i)].add(perm_to_one_str(perm))
    for key in examples:
        examples[key] = list(examples[key])
    obj["tile"] = tiles
    obj["examples"] = examples
    obj["rank"] = max(tiling.rank() for tiling in cover)
    obj["avoid"] = avoids_to_delimited(cover.input_set)
    obj["length"] = len(cover.input_set.basis)
    return obj

def json_to_tiling(json_object):
    if json_object["avoid"] == "e":
        basis = [Perm(())]
    elif json_object["avoid"] == "o":
        basis = "o"
    else:
        basis = [Perm(list(x)) for x in json_object["avoid"].split("_")]

    tilings = []
    for block in json_object["tile"]:
        tiling_dict = dict()
        for item in block:
            point = tuple(item["point"])
            val = item["val"]

            if val in ["point", "o", "p", "P"]:
                val = Block.point
            elif val in ["decreasing", "\\", "d", "D"]:
                val = Block.decreasing
            elif val in ["increasing", "/", "i", "I"]:
                val = Block.increasing
            elif val in ["self", "X", "x", "r", "R"]:
                val = "input_set"
            elif val[:2] in ["Av", "av", "AV"]:
                val = av_string_to_permset(val)

            tiling_dict[point] = val
        tilings.append(Tiling(tiling_dict))
    return tilings

def process_folder(folder_name):
    for dirpath, dirnames, filenames in os.walk(folder_name):
        for filename in filenames:
            cover = parse_log(os.path.join(dirpath, filename), file=True)
            c = cover_to_json(cover)
            mongo.permsdb.perm.insert(c)

if __name__ == '__main__':
    #print(tiling_to_json([Tiling({ (0,0): PermSet.avoiding(Perm.one([1,2,3])) }),
    #                      Tiling({ (0,3): Block.point, (1,0): Block.point, (2,1): PermSet.avoiding([Perm.one([1,2])]), (3,4): Block.point, (4,2): Block.point })]))
    #print(parse_log('/data/henningu/length19/1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_2413_2431_3124_3142_3214_3241_4123_4132_4213.txt', file=True))
    #print(parse_log('../../Parse/ex9_output.txt', file=True))

    #res = permset_to_av_string(PermSet.avoiding([ Perm.one([1,2,3,4]), Perm.one([4,3,2,1]), Perm.one([4,1,3,2]) ]))
    process_folder("/Users/viktor/Google Drive/lokaverkefni/Parse/bla")
    p = Perm.one([1,2,3])
    c = parse_log('/Users/viktor/Google Drive/lokaverkefni/Parse/bla/1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_2413_2431_3124_3142_3241.txt', file=True)
