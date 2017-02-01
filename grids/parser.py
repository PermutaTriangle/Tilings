from re import split, search, M
from pprint import pprint
from Tiling import Block, Tiling, PermSetTiled
from permuta import PermSet, Perm
from permuta.misc import flatten
from collections import defaultdict

def parse_log(inp, file=False):
    tilings = []
    if file:
        with open(inp) as f:
            inp = f.read()
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
        print("blaasdfadsfafsdadfsafdsadfsasdfadsfadsfadsfasfasfafsdsadfafsd", el)
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
                num, avoids = i.split(': ')
                # Remove "Av()"
                avoids = avoids[3:-1]
                # Get 2d array
                avoids = eval(avoids)
                avoids = PermSet.avoiding([ Perm.one(perm) for perm in avoids ])
                permsets[num] = avoids
        for i in range(len(table)):
            for j in range(len(table[i])):
                char = table[i][j]
                if char == 'X':
                    rule[(i, j)] = 'input_set'
                elif char.isnumeric():
                    rule[(i, j)] = permsets.get(char, None)
                elif char == 'o':
                    rule[(i, j)] = Block.point
        tilings.append(Tiling(rule))
    return tilings

def tiling_to_json(tilings):
    example_json_structure = {
        "_id" : 'ObjectId("5882153c7e98af0c473a874e")',
        "avoid" : "o",
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
    for tiling in tilings:
        tile = []
        for k, v in tiling.items():
            point = {}
            point['point'] = [*k]
            point['val'] = repr(v)
            tile.append(point)
        tiles.append(tile)
    obj['tile'] = tiles

    # Create examples
    examples = {}
    for i in range(6):
        if not str(i) in examples:
            # Set of all length i permutations
            examples[str(i)] = set()
        for T in tilings:
            for perm in PermSetTiled(T).of_length(i):
                examples[str(i)].add(perm)
    for i in examples['4']:
        print(i)




if __name__ == '__main__':
    #print(tiling_to_json([Tiling({ (0,0): PermSet.avoiding(Perm.one([1,2,3])) }),
    #                      Tiling({ (0,3): Block.point, (1,0): Block.point, (2,1): PermSet.avoiding([Perm.one([1,2])]), (3,4): Block.point, (4,2): Block.point })]))
    print(parse_log('../1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_2413_2431_3124_3142_3214_3241_4123_4132_4213.txt', file=True))
    #print(parse_log('../../Parse/ex9_output.txt', file=True))
