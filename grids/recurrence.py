from Cover import Cover
from Tiling import Block, Tiling
from permuta import *
from pymongo import MongoClient
from collections import defaultdict

def find_recurrence(cover):
    minbase = 0
    basecases = defaultdict(int)
    static = [True]*len(cover)
    points = [0]*len(cover)
    sets = [[] for i in range(len(cover))]
    # find minimum base cases needed and mark non-recursive tilings
    for i,tiling in enumerate(cover):
        for k,v in tiling.items():
            if v == Block.point:
                points[i] += 1
            else:
                sets[i].append(v)
        static[i] = (len(sets[i]) == 0)
        if static[i]:
            minbase = max(minbase,points[i])
    
    # set base cases by counting
    for i in range(minbase+1):
        basecases[i] = len(cover.of_length(i))

    # create latex for recurrence
    rlist = []
    av = ord('b') 
    avrec = {'a':cover.input_set}
    recav = {cover.input_set:'a'}
    for i,tiling in enumerate(cover): 
        if static[i]:
            continue
        c = ord('i')
        slist = []
        vlist = []
        for s in sets[i]:
            # add unseen sets to dictionaries for lookup
            if s not in recav:
                avrec[chr(av)] = s
                recav[s] = chr(av)
                av += 1
            setrec = recav[s]
            # add the sum for this set
            slist.append("\\sum_{" + chr(c) + "=0}^{" + "-".join(["n"] + [chr(j) for j in range(ord('i'), c)] + ([str(points[i])] if points[i] > 0 else [])) + "}")
            vlist.append(setrec+"_{" + chr(c) + "}") 
            c += 1
        # remove last sum
        slist.pop()
        # calculate the length the last set uses
        vlist[-1] = vlist[-1][:2] + "{" + "-".join(["n"] + [chr(j) for j in range(ord('i'), c-1)] + ([str(points[i])] if points[i] > 0 else [])) + "}"
        rlist.append("".join(slist) + "".join(vlist))
    latex = "+".join(rlist)
    return dict(basecases), latex, recav

if __name__ == "__main__":
    input_set = PermSet.avoiding([Perm.one([1,2])])
    b = Tiling({})
    c = Tiling({(0,0): Block.point, (1,1): input_set})
    g = Cover(input_set, [b,c])

    input_set2 = PermSet.avoiding(Perm.one([1,3,2]))
    d = Tiling({(1,0):Block.point, (0,1):input_set2, (2,2):input_set2})
    f = Cover(input_set2, [b,d])

    input_set3 = PermSet.avoiding(Perm.one([1,2,3,4]))
    e = Cover(input_set3, [b,c,d])
    
    i = Tiling({(0,0): input_set3, (1,1): input_set3, (2,2): input_set2, (3,3): input_set})
    h = Cover(input_set2, [i])
    print(find_recurrence(g))
    print(find_recurrence(f))
    print(find_recurrence(e))
    print(find_recurrence(h))
