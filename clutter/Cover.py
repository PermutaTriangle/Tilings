# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is

import warnings

from builtins import list
from operator import itemgetter
from permuta import Perm
from permuta import PermSet
from permuta.misc import ordered_set_partitions, flatten
from permuta.descriptors import Descriptor
from Tiling import PermSetTiled
from Tiling import Block
from collections import defaultdict
from math import factorial


#TODO: Find a better place for these methods
def permset_to_av_string(permset):
    """Takes the basis of the PermSet, converts the Perms to one based then into lists"""
    arr = [list([ i + 1 for i in perm ]) for perm in permset.basis]
    return 'Av({})'.format(str( arr ))

def perm_to_one_str(perm):
    return "".join([str(1 + i) for i in list(perm)])

def avoids_to_delimited(permset, delim='_'):
    return delim.join([perm_to_one_str(perm) for perm in permset.basis])


class Cover(list):
    """Cover class.

    Tilings are stored in an array in size order.
    """

    input_set = PermSet()
    def __init__(self, input_set, tilings=[]):
        """Accepts a list of Tilings"""
        list.__init__(self, tilings) 
        self.sort(key = lambda tiling: ((tiling._max_i+1)*(tiling._max_j+1), tiling._max_i, tiling.rank()))
        self.input_set = input_set
        self.rank = max(tiling.rank() for tiling in self)


    def __repr__(self):
        format_string = "<A cover of {} tilings>"
        return format_string.format(len(self))

    def __str__(self):
        pass

    def of_length(self, num):
        # Create examples
        ret = []
        for T in self:
            #print(T)
            for perm in PermSetTiled(T).of_length(num):
                ret.append(perm)
        return ret

    def to_json(self):
        ''' 
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
        '''
        obj = {}
        tiles = []
        for T in self:
            tile = []
            for k, v in T.items():
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
            for T in self:
                for perm in PermSetTiled(T).of_length(i):
                    examples[str(i)].add(perm_to_one_str(perm))
        for key in examples:
            examples[key] = list(examples[key])
        obj["tile"] = tiles
        obj["examples"] = examples
        obj["rank"] = self.rank
        obj["avoid"] = avoids_to_delimited(self.input_set)
        obj["length"] = len(self.input_set.basis)
        basecases,latex,recav,avrec = self.find_recurrence()
        recurrence = {}
        for k,v in basecases.items():
            recurrence[str(k)] = str(v)
        recurrence["n"] = latex
        obj["recurrence"] = recurrence
        depends = {}
        for k,v in avrec.items():
            depends[k] = permset_to_av_string(v)
        obj["depends"] = depends
        revdepends = {}
        for k,v in recav.items():
            revdepends[permset_to_av_string(k)] = v
        obj["revdepends"] = revdepends
        coeffs = []
        for i in range(11):
            coeffs.append(len(self.of_length(i)))
        obj["coeffs"] = coeffs
        
        # TODO add recurrence avoidance class map to json
        return obj
	
    def find_recurrence(self):
        minbase = 0
        basecases = defaultdict(int)
        static = [True]*len(self)
        points = [0]*len(self)
        sets = [[] for i in range(len(self))]
        maxi,maxj=1,1
        # find minimum base cases needed and mark non-recursive tilings
        for i,tiling in enumerate(self):
            for k,v in tiling.items():
                maxi = max(maxi, k[0]+1)
                maxj = max(maxj, k[1]+1)
                if v == Block.point:
                    points[i] += 1
                else:
                    sets[i].append(v)
            static[i] = (len(sets[i]) == 0)
            minbase = max(minbase,points[i])
        
        # set base cases by counting
        for i in range(minbase+1):
            basecases[i] = len(self.of_length(i))

        # create latex for recurrence
        rlist = []
        av = ord('b') 
        avrec = {'/':Block.increasing,'\\':Block.decreasing}
        recav = {Block.increasing:'/',Block.decreasing:'\\'}
        if self.input_set != Block.increasing and self.input_set != Block.decreasing:
            avrec['a'] = self.input_set
            recav[self.input_set] = 'a'
        inc,dec = False,False

        if all(static):
            del avrec['/']
            del recav[Block.increasing]

            del avrec['\\']
            del recav[Block.decreasing]
            
            return dict(basecases), "0", recav, avrec
        
        for i,tiling in enumerate(self): 
            if static[i]:
                continue
            rows = [(0,0)]*maxi
            columns = [(0,0)]*maxj
            for k,v in tiling.items():
                if v == Block.point:
                    rows[k[0]] = (rows[k[0]][0]+1, rows[k[0]][1])
                    columns[k[1]] = (columns[k[1]][0]+1, columns[k[1]][1])
                else:
                    rows[k[0]] = (rows[k[0]][0], rows[k[0]][1]+1)
                    columns[k[1]] = (columns[k[1]][0], columns[k[1]][1]+1)
            c = ord('i')
            slist = []
            vlist = []
            muli = 1
            mull = []
            
            #table storing which iterator variable is used by which set (in respective cell)
            its = [['' for j in range(maxj)] for i in range(maxi)]

            for k,s in tiling.items():
                if s == Block.point:
                    continue
                # add unseen sets to dictionaries for lookup
                if s not in recav:
                    avrec[chr(av)] = s
                    recav[s] = chr(av)
                    av += 1
                setrec = recav[s]
                # add the sum for this set
                slist.append( (chr(c) + "=0", "-".join( ["n"] + [chr(j) for j in range(ord('i'), c)] + ([str(points[i])] if points[i] > 0 else [] ) ) ) )
                if s == Block.increasing:
                    inc = True
                elif s == Block.decreasing:
                    dec = True
                else:
                    vlist.append((setrec,chr(c))) 
                its[k[0]][k[1]] = chr(c) 
                c += 1
            
            blist = []
            removeFromBList = False
            for y in range(maxi):
                row = rows[y]
                if row[1] > 0:
                    sub = points[i] - row[0]
                    choices = [chr(j) for j in range(ord('i'), c)]
                    for x in range(maxj):
                        try:
                            choices.remove(its[y][x])
                        except ValueError:
                            pass
                    if row[0]:
                        blist.append( ('-'.join(['n']+choices+[str(sub)]), str(row[0])) )
                        sub += row[0]
                    if row[1] > 1:
                        for x in range(maxj):
                            item = its[y][x]
                            if item == '':
                                continue
                            blist.append(('-'.join(['n']+choices+[str(sub)]),  item))
                            choices.append(item)
                            choices.sort()
                            removeFromBList = True
                muli *= factorial(row[0]) 
            for x in range(maxj):
                col = columns[x]
                if col[1] > 0:
                    sub = points[i] - col[0]
                    choices = [chr(j) for j in range(ord('i'), c)]
                    for y in range(maxi):
                        try:
                            choices.remove(its[y][x])
                        except ValueError:
                            pass
                    if col[0]:
                        blist.append(('-'.join(['n']+choices+[str(sub)]), str(col[0])))
                        sub += col[0]
                    if col[1] > 1:    
                        for y in range(maxi):
                            item = its[y][x]
                            if item == '':
                                continue
                            blist.append(('-'.join(['n']+choices+[str(sub)]), item))
                            choices.append(item)
                            choices.sort()
                            removeFromBList = True
                muli *= factorial(col[0])

            if removeFromBList and blist:
                blist.pop()
            # remove last sum
            if slist:
                slist.pop()
            # calculate the length the last set uses
            if vlist:
                vlist[-1] = (vlist[-1][0],"-".join(["n"] + [chr(j) for j in range(ord('i'), c-1)] + ([str(points[i])] if points[i] > 0 else [])))
            rlist.append(self.__term(slist,vlist,blist,muli))
       
        addend = 0
        latex = []
        for it in rlist:
            try:
                addend += int(it)
            except:
                latex.append(it)

        latex = "+".join(latex + ([str(addend)] if addend else []))
        if not latex:
            latex = "0"
        
        if not inc:
            del avrec['/']
            del recav[Block.increasing]

        if not dec:
            del avrec['\\']
            del recav[Block.decreasing]

        return dict(basecases), latex, recav, avrec


    def __term(self,slist = [], vlist = [], blist = [], muli = 1):
        if not slist and not vlist and not blist:
            return str(muli)
        elif len(slist) == 1 and not vlist and not blist:
            i,n = slist[0]
            sm = n + '+1'
            if muli != 1:
                sm = str(muli)+'('+sm+')'
            return sm
        elif len(slist) == 1 and not vlist and len(blist) == 1:
            i,n1 = slist[0]
            n,k = blist[0]
            try:
                ik = int(k)
            except:
                sm = '2^{' + n + '}'
                if muli != 1:
                    sm = str(muli) + "\cdot" + sm
                return sm
        slist = ["\\sum_{"+a+"}^{"+b+"}" for a,b in slist]
        vlist = [a+"_{"+b+"}" for a,b in vlist]
        blist = ["\\binom{"+a+"}{"+b+"}" for a,b in blist]
        return "".join(slist) + (str(muli) if (not vlist and not blist) or muli != 1 else "") + "".join(vlist) + "".join(blist)
  



if __name__ == "__main__":
    from Cover import Cover
    from Tiling import Tiling, Block
    b = Tiling({(0,0): Block.point, (1,1): Block.point})
    c = Tiling({(0,1): Block.point, (1,0): Block.point})
    d = Tiling({(0,0): Block.point, (1,1): Block.decreasing, (2,2): Block.increasing})
    from permuta import PermSet, Perm
    g = Cover(PermSet.avoiding([Perm.one([1,4,3,2])]), [d, c])

    print(g.__repr__())
    print(g.of_length(2))
    print(g.to_json())
