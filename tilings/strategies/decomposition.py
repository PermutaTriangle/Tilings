from tilings.algorithms import (Factor, FactorWithInterleaving,
                                FactorWithMonotoneInterleaving)


def general_factor(tiling, factor_class, union=False, **kwargs):
    """
    Iterator of factor strategy.
    """
    assert factor_class in [Factor, FactorWithMonotoneInterleaving,
                            FactorWithInterleaving]
    workable = kwargs.get('workable', True)
    factor_algo = factor_class(tiling)
    if factor_algo.factorable():
        yield factor_algo.rule(workable=workable)
        if union:
            yield from factor_algo.all_union_rules()


def factor(tiling, **kwargs):
    return general_factor(tiling, Factor, **kwargs)


def factor_with_monotone_interleaving(tiling, **kwargs):
    return general_factor(tiling, FactorWithMonotoneInterleaving, **kwargs)


def factor_with_interleaving(tiling, **kwargs):
    return general_factor(tiling, FactorWithInterleaving, **kwargs)


def unions_of_factor(tiling, **kwargs):
    return general_factor(tiling, Factor, union=True, **kwargs)


def unions_of_factor_with_monotone_interleaving(tiling, **kwargs):
    return general_factor(tiling, FactorWithMonotoneInterleaving, union=True,
                          **kwargs)


def unions_of_factor_with_interleaving(tiling, **kwargs):
    return general_factor(tiling, FactorWithInterleaving, union=True, **kwargs)
