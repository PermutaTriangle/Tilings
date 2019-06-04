"""Functions for adding and removing from database."""
import json
from functools import partial

import sympy
from pymongo import MongoClient, errors
from sympy import Poly, abc, sympify, var

from comb_spec_searcher import ProofTree
from comb_spec_searcher.utils import check_equation, check_poly
from permuta import Perm

from .misc import is_tree


def taylor_expand(genf, n=10):
    """Return a list of the first n coefficients of genf's taylor expansion."""
    genf = simplify(genf)
    ser = Poly(genf.series(n=n+1).removeO(), abc.x)
    res = ser.all_coeffs()
    res = res[::-1] + [0]*(n+1-len(res))
    return res


def simplify(genf):
    """Try to write genf as a fraction and then simplify."""
    num, den = genf.as_numer_denom()
    num = num.expand()
    den = den.expand()
    genf = num/den
    return genf.simplify()


def tiling_symmetries(tiling):
    """Return a set of the symmetries of a tiling."""
    return set([tiling.rotate90(), tiling.rotate180(),
                tiling.rotate270(), tiling.inverse(),
                tiling.complement(), tiling.antidiagonal(),
                tiling.reverse(), tiling])


def update_database(tiling, min_poly, genf, tree, force=False, equations=None):
    """
    Add the generating function genf for tiling to database.

    The generating function is verified to be correct up to length 10.
    Each database entry has three things: tiling, genf, tree.
    """
    try:
        mongo = MongoClient('mongodb://localhost:27017/permsdb_three')

        if not force:
            info = mongo.permsdb_three.min_poly_db.find_one({'key':
                                                            tiling.compress()})
            if info is not None:
                return
        if isinstance(genf, str):
            genf = sympify(genf)
        if isinstance(min_poly, str):
            min_poly = sympify(min_poly)
        assert isinstance(tree, ProofTree) or tree is None
        if genf is None and min_poly is None:
            raise ValueError("Not adding genf or min poly.")

        verify = 4
        count = [len(list(tiling.objects_of_length(i)))
                 for i in range(verify + 1)]
        if genf is not None:
            if taylor_expand(sympify(genf), verify) != count:
                print(taylor_expand(sympify(genf), verify), count)
                raise ValueError("Incorrect generating function.")

        if min_poly is not None:
            if (not check_poly(min_poly, count) and
                    not check_equation(min_poly, count)):
                raise ValueError("Incorrect minimum polynomial.")

        for t in tiling_symmetries(tiling):
            info = {'key': t.compress()}
            if equations is not None:
                info['eqs'] = equations
            elif tree is not None:
                try:
                    equations = ",\n".join("{} = {}".format(str(eq.lhs),
                                                            str(eq.rhs))
                                           for eq in tree.get_equations())
                    equations = equations.replace("(x)", "")
                    info['eqs'] = equations
                except ValueError as e:
                    pass
            if tree is not None:
                info['tree'] = json.dumps(tree.to_jsonable())
            if min_poly is not None:
                info['min_poly'] = str(min_poly)
            if genf is not None:
                info['genf'] = str(genf)
            mongo.permsdb_three.min_poly_db.update({'key': info['key']},
                                                   info, upsert=True)
    except errors.PyMongoError:
        raise ValueError(("If you wish to save generating functions of tilings"
                          " you will need to setup MongoDB."))


def check_database(tiling, update=True):
    """Look up and return the database entry for tiling.
    This is a dictionary containing:
        key: the compression of the tiling
        min_poly: the minimum polynomial satisfied by the tiling
        genf: the generating function for the tiling
        tree: a proof tree for the enumeration of the tiling"""
    try:
        mongo = MongoClient('mongodb://localhost:27017/permsdb_three')
        info = mongo.permsdb_three.min_poly_db.find_one({'key':
                                                         tiling.compress()})
    except errors.PyMongoError:
        raise ValueError(("If you wish to find the generating functions of "
                          "tilings you will need to setup MongoDB. If you "
                          "need a copy of the database computed by the "
                          "Permuta Triangle group contact "
                          "permutatriangle@gmail.com"))

    if info is None:
        error = "Tiling not in database."
        if update:
            if len(tiling.find_factors()) > 1:
                error += " Try factoring tiling first."
            elif tiling.requirements:
                error += " Try special casing requirements first."
            elif any(not ob.is_single_cell() for ob in tiling.obstructions):
                error += (" Current methods to enumerate factors can't handle "
                          "non-local obstructions.")
            elif tiling.dimensions == (1, 1):
                return enumerate_one_by_one(tiling)
            elif is_monotone_tree_factor(tiling):
                return enumerate_monotone_tree_factor(tiling)
            elif is_monotone_tree_factor(tiling, one_non_monotone=True):
                f = enumerate_tree_factor(tiling)
                update_database(tiling, None, f, None)
                return check_database(tiling)
            else:
                error += "No method to enumerate tiling."

        raise ValueError(error)
    return info


def is_monotone_tree_factor(tiling, one_non_monotone=False):
    """Return True if a monotone tree factor. If one_non_monotone=True,
    then allow one cell to be non monotone."""
    basis_array = tiling.cell_basis()
    cell_graph = tiling.cell_graph()
    if not is_tree(cell_graph):
        return False
    start = None
    incr = Perm((0, 1))
    decr = Perm((1, 0))
    for cell, basis in basis_array.items():
        if basis[1]:
            return False
        basis = basis[0]
        if ((len(basis) == 1 and len(basis[0]) == 1) or
                (incr in basis or decr in basis)):
            # looking for non-monotone starting point
            continue
        if start is None:
            if one_non_monotone:
                start = cell
            else:
                return False
        else:
            return False
    return True


def enumerate_monotone_tree_factor(tiling):
    """Return min_poly, genf, tree, that enumerates a monotone tree factor."""
    try:
        import tilescopethree as t
        from tilescopethree.strategies import (row_placements,
                                               col_placements,
                                               one_by_one_verification,
                                               factor,
                                               requirement_corroboration,
                                               row_and_column_separation,
                                               obstruction_transitivity)
        from comb_spec_searcher import StrategyPack
    except ImportError:
        raise ValueError(("The enumeration of tilings relies on tilescope."
                          " This has not yet be released. If you need this "
                          "functionality, then contact "
                          "permutatriangle@gmail.com"))
    pack = StrategyPack(initial_strats=[factor,
                                        requirement_corroboration],
                        inferral_strats=[row_and_column_separation,
                                         obstruction_transitivity],
                        expansion_strats=[[partial(col_placements,
                                                   positive=False),
                                           partial(row_placements,
                                                   positive=False)]],
                        ver_strats=[one_by_one_verification],
                        name="restricted_row_col_placements")
    searcher = t.TileScopeTHREE(tiling, pack)
    tree = searcher.auto_search()
    min_poly, genf = tree.get_min_poly(solve=True)
    update_database(tiling, min_poly, genf, tree, force=True)
    return check_database(tiling)


def enumerate_one_by_one(tiling):
    """Try to add the enumeration of a one by one tiling to the database,
    by starting a tilescpe run using a point placement pack."""
    try:
        import tilescopethree as t

        basis = [ob.patt for ob in tiling.obstructions]
        if any((len(patt) == 3 and
                not patt.is_increasing() and
                not patt.is_decreasing()) for patt in basis):
            from tilescopethree.strategies import (
                                all_factor_insertions, factor,
                                requirement_placement, one_by_one_verification,
                                root_requirement_insertion,
                                row_and_column_separation,
                                requirement_corroboration,
                                subset_verified, globally_verified)
            from comb_spec_searcher import StrategyPack
            # 231-avoiding
            pack = StrategyPack(
                    initial_strats=[factor, requirement_corroboration,
                                    partial(all_factor_insertions,
                                            ignore_parent=True)],
                    inferral_strats=[row_and_column_separation],
                    expansion_strats=[[partial(root_requirement_insertion,
                                               maxreqlen=1)],
                                      [requirement_placement]],
                    ver_strats=[one_by_one_verification],
                    name="subclass_of_231")
        else:
            pack = t.strategy_packs_v2.all_the_strategies
    except ImportError:
        raise ValueError(("The enumeration of tilings relies on tilescope."
                          " This has not yet be released. If you need this "
                          "functionality, then contact "
                          "permutatriangle@gmail.com"))
    searcher = t.TileScopeTHREE(tiling, pack)
    tree = searcher.auto_search(status_update=10)
    min_poly, genf = tree.get_min_poly(solve=True)
    update_database(tiling, min_poly, genf, tree)
    return check_database(tiling)


def enumerate_tree_factor(tiling, **kwargs):
    """
    Return generating function of a factor whose cell graph is a treeself.

    The factor can contain at most one non-monotone class.
    """
    basis_array = tiling.cell_basis()
    cell_graph = tiling.cell_graph()
    if not is_tree(cell_graph):
        raise ValueError(("Can only enumerate factors whose cell graph is a"
                          "tree."))
    start = None
    incr = Perm((0, 1))
    decr = Perm((1, 0))
    for cell, basis in basis_array.items():
        if basis[1]:
            raise ValueError("Only enumerate factor with no requirements.")
        basis = basis[0]
        if ((len(basis) == 1 and len(basis[0]) == 1) or
                (incr in basis or decr in basis)):
            # looking for non-monotone starting point
            continue
        if start is None:
            start = cell
        else:
            raise ValueError("Can only handle one non-monotone cell.")
    # variable for every cell
    variables = [var(["v_{}{}".format(i, j)
                      for j in range(tiling.dimensions[1])])
                 for i in range(tiling.dimensions[0])]
    if start is None:
        # pick some non-empty starting point
        for start, basis in basis_array.items():
            if len(basis[0][0]) != 1:
                break
    from tilings import Obstruction, Tiling
    basis = basis_array[start]
    y = variables[start[0]][start[1]]
    initial_genf = Tiling([Obstruction.single_cell(p, (0, 0))
                           for p in basis[0]]).get_genf().subs({abc.x: y})
    return enumerate_tree_factor_helper(basis_array, cell_graph, initial_genf,
                                        variables, {start},
                                        [(start, True), (start, False)],
                                        **kwargs)


def enumerate_tree_factor_helper(basis_array, cell_graph, genf,
                                 variables, visited, queue, **kwargs):
    """
    The heart of factor enumeration function.

    It will take the first entry of the queue, which is a tuple (cell, row)
    where cell is the cell we are working on and row is a boolean that tells
    you to either enumerate its row or column.
    """
    while queue:
        start_cell, row = queue.pop(0)
        col_index, row_index = start_cell
        if row:
            row_vars = [v[row_index] for v in variables]
        else:
            row_vars = [v for v in variables[col_index]]
        for cell, basis in basis_array.items():
            basis = basis[0]
            if len(basis) == 1 and len(basis[0]) == 1:
                # ignore empty cells
                continue
            if not ((row and cell[1] == row_index) or
                    (not row and cell[0] == col_index)):
                # ignore if not in correct row/col
                continue
            if cell in visited:
                # ignore is already counted
                continue
            else:
                visited.add(cell)
                # we will come back and enumerate the cells col/row later.
                queue.append((cell, not row))
            y = variables[cell[0]][cell[1]]
            substitutions = {v: v/(1 - y) for v in row_vars if v != y}
            genf = simplify((genf.subs(substitutions)/(1 - y)))
            if len(basis) != 1:
                # We have a finite cell, so want the y^0, y^1, ..., y^k terms.
                max_length = max(len(p) for p in basis)
                new_genf = 0
                temp_genf = genf
                for i in range(max_length):
                    new_genf += temp_genf.subs({y: 0}) * y ** i
                    temp_genf = ((genf - new_genf)/y**(i + 1))
                    temp_genf = simplify(temp_genf)
                genf = new_genf

    subs = kwargs.get('substitute', True)
    # make it look a little bit nice
    if subs:
        genf = simplify(genf.subs({v: abc.x for vs in variables for v in vs}))
    else:
        genf = simplify(genf), variables
    return genf
