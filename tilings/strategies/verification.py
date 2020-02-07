from tilings.algorithms.enumeration import (BasicEnumeration,
                                            DatabaseEnumeration,
                                            ElementaryEnumeration,
                                            LocalEnumeration,
                                            LocallyFactorableEnumeration,
                                            OneByOneEnumeration)


def verify_basic(tiling, **kwargs):
    """
    Verify the most basics tilings.
    """
    return BasicEnumeration(tiling).verification_rule()


def verify_one_by_one(tiling, basis, **kwargs):
    """Return a verification if one-by-one verified."""
    return OneByOneEnumeration(tiling, basis).verification_rule()


def verify_database(tiling, **kwargs):
    """Verify a tiling that is in the database"""
    return DatabaseEnumeration(tiling).verification_rule()


def verify_locally_factorable(tiling, **kwargs):
    """
    The locally factorable verified strategy.

    A tiling is globally verified if every requirement and obstruction is
    non-interleaving.
    """
    return LocallyFactorableEnumeration(tiling).verification_rule()


def verify_elementary(tiling, **kwargs):
    """
    A tiling is elementary verified if it is locally factorable
    and has no interleaving cells.
    """
    return ElementaryEnumeration(tiling).verification_rule()


def verify_local(tiling, no_reqs=False, **kwargs):
    """
    The local verified strategy.

    A tiling is local verified if every obstruction and every requirement is
    localized and the tiling is not 1x1.
    """
    return LocalEnumeration(tiling, no_reqs).verification_rule()
