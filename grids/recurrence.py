from grids import *
from permuta import *
from pymongo import MongoClient
from collections import defaultdict

def find_recurrence(avoids):
    client = MongoClient('mongodb://webapp:c73f12a3@localhost:27017/permsdb')
    permsdb = client.permsdb
    collection = permsdb.perm
    val = collection.find_one({"avoid":avoids})
    tilings = val['tile']
    rank = val['rank']
    if rank > 2:
        raise NotImplementedError("Only supports covers of rank 2 or lower")
    minbase = -1
    basecases = defaultdict(int)
    static = [True]*len(tilings)
    points = [0]*len(tilings)
    sets = [[] for i in range(len(tilings))]
    # find minimum base cases needed and mark non-recursive tilings
    for i,tiling in enumerate(tilings):
        for item in tiling:
            if item['val'] == 'o':
                points[i] += 1
            else:
                sets[i].append(item['val'])
        static[i] = (len(sets[i]) == 0)
        if static[i]:
            minbase = max(minbase,points[i])
            basecases[points[i]] += 1
    

    for i,tiling in enumerate(tilings):
        if static[i]:
            continue
        # do recursive base case filling

    
            

    print(minbase)
    print(static)
    print(points)
    print(sets)
    print(dict(basecases))
    
    return

if __name__ == "__main__":
    find_recurrence("132")
