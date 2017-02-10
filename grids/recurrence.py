from Cover import Cover
from Tiling import Block, Tiling
from permuta import *
from pymongo import MongoClient
from collections import defaultdict
from math import factorial

def find_recurrence(cover):
    minbase = 0
    basecases = defaultdict(int)
    static = [True]*len(cover)
    points = [0]*len(cover)
    sets = [[] for i in range(len(cover))]
    maxi,maxj=1,1
    # find minimum base cases needed and mark non-recursive tilings
    for i,tiling in enumerate(cover):
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
        basecases[i] = len(cover.of_length(i))

    # create latex for recurrence
    rlist = []
    av = ord('b') 
    avrec = {'a':cover.input_set}
    recav = {cover.input_set:'a'}
    for i,tiling in enumerate(cover): 
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
            slist.append("\\sum_{" + chr(c) + "=0}^{" + "-".join(["n"] + [chr(j) for j in range(ord('i'), c)] + ([str(points[i])] if points[i] > 0 else [])) + "}")
            vlist.append(setrec+"_{" + chr(c) + "}") 
            its[k[0]][k[1]] = chr(c) 
            c += 1
        
        blist = []

        for y in range(maxi):
            row = rows[y]
            if row[1] > 1:
                sub = points[i] - row[0]
                choices = [chr(j) for j in range(ord('i'), c)]
                for x in range(maxj):
                    try:
                        choices.remove(its[y][x])
                    except ValueError:
                        pass
                if row[0]:
                    blist.append("\\binom{" + '-'.join(['n']+choices+[str(sub)]) + "}{" + str(row[0]) + "}")
                    sub += row[0]
                for x in range(maxi):
                    item = its[y][x]
                    if item == '':
                        continue
                    blist.append("\\binom{" + '-'.join(['n']+choices+[str(sub)]) + "}{" + item  + "}")
                    choices.append(item)
                    choices.sort()
            muli *= factorial(row[0]) 
        for x in range(maxj):
            col = columns[x]
            if col[1] > 1:
                sub = points[i] - col[0]
                choices = [chr(j) for j in range(ord('i'), c)]
                for y in range(maxi):
                    try:
                        choices.remove(its[y][x])
                    except ValueError:
                        pass
                if col[0]:
                    blist.append("\\binom{" + '-'.join(['n']+choices+[str(sub)]) + "}{" + str(col[0]) + "}")
                    sub += col[0]
                for y in range(maxi):
                    item = its[y][x]
                    if item == '':
                        continue
                    blist.append("\\binom{" + '-'.join(['n']+choices+[str(sub)]) + "}{" + item  + "}")
                    choices.append(item)
                    choices.sort()
            muli *= factorial(col[0])
        if blist:
            blist.pop()
        # remove last sum
        if slist:
            slist.pop()
        # calculate the length the last set uses
        if vlist:
            vlist[-1] = vlist[-1][:2] + "{" + "-".join(["n"] + [chr(j) for j in range(ord('i'), c-1)] + ([str(points[i])] if points[i] > 0 else [])) + "}"
        rlist.append("".join(slist) + (str(muli) if muli != 1 else "") + "".join(vlist) + "".join(blist))
        latex = "+".join(rlist)
    return dict(basecases), latex, recav, avrec

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
