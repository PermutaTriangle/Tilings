import json

from sympy import sympify, Poly, abc

from pymongo import MongoClient

mongo = MongoClient('mongodb://localhost:27017/permsdb_three')


def taylor_expand(genf, n=10):
    """Return a list of the first n coefficients of genf's taylor expansion"""
    num, den = genf.as_numer_denom()
    num = num.expand()
    den = den.expand()
    genf = num/den
    ser = Poly(genf.series(n=n+1).removeO(), abc.x)
    res = ser.all_coeffs()
    res = res[::-1] + [0]*(n+1-len(res))
    return res

def tiling_symmetries(tiling):
    """Return a set of the symmetries of a tiling."""
    return set([tiling.rotate90(), tiling.rotate180(),
                tiling.rotate270(), tiling.inverse(),
                tiling.complement(), tiling.antidiagonal(),
                tiling.reverse(), tiling])

def update_database(tiling, genf, tree):
    """
    Add the generating function genf for tiling to database.

    The generating function is verified to be correct up to length 10.
    Each database entry has three things: tiling, genf, tree.
    """
    if isinstance(genf, str):
        genf = sympify(genf)

    count = [len(list(tiling.objects_of_length(i))) for i in range(11)]
    if taylor_expand(sympify(genf), 10) != count:
        raise ValueError("Incorrect generating function.")

    for t in tiling_symmetries(tiling):
        info = {'key': t.compress(), 'genf': str(genf),
                'tree': json.dumps(tree.to_jsonable())}

        mongo.permsdb_three.factordb.update({'key': info['key']},
                                            info, upsert=True)

def check_database(tiling):
    """Look up and return the generating function for tiling."""
    info = mongo.permsdb_three.factordb.find_one({'key': tiling.compress()})
    if info is None:
        raise ValueError()
    return sympify(info['genf'])
