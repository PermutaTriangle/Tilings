from pymongo import MongoClient
import json
from sympy import sympify
mongo = MongoClient('mongodb://localhost:27017/permsdb_three')


def update_database(tiling, genf, tree):
    info = {'key': tiling.compress(), 'genf': str(genf),
            'tree': json.dumps(tree.to_jsonable())}
    mongo.permsdb_three.factordb.update({'key': info['key']}, info, upsert=True)

def check_database(tiling):
    print(tiling)
    info = mongo.permsdb_three.factordb.find_one({'key': tiling.compress()})
    if info is None:
        raise ValueError()
    return sympify(info['genf'])
