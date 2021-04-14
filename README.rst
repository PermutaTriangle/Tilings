Tilings
=======

.. image:: https://travis-ci.org/PermutaTriangle/Tilings.svg?branch=master
    :alt: Travis
    :target: https://travis-ci.org/PermutaTriangle/Tilings
.. image:: https://coveralls.io/repos/github/PermutaTriangle/Tilings/badge.svg?branch=master
    :alt: Coveralls
    :target: https://coveralls.io/github/PermutaTriangle/Tilings?branch=master
.. image:: https://img.shields.io/pypi/v/Tilings.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/Tilings
.. image:: https://img.shields.io/pypi/l/Tilings.svg
    :target: https://pypi.python.org/pypi/Tilings
.. image:: https://img.shields.io/pypi/pyversions/Tilings.svg
    :target: https://pypi.python.org/pypi/Tilings
.. image:: https://requires.io/github/PermutaTriangle/Tilings/requirements.svg?branch=master
     :target: https://requires.io/github/PermutaTriangle/Tilings/requirements/?branch=master
     :alt: Requirements Status


The ``tilings`` Python library contains code for working with gridded
permutations and tilings, and in particular the ``TileScope`` algorithm, which
can be used to enumerate permutation classes.

If you are primarily interested in enumerating permutation classes, then you
may wish to skip ahead to the ``TileScope`` section, but note the installation
will be the same as for ``tilings``.

If you need support, have a suggestion, or just want to be up to date with the
latest developments please join us on our
`Discord server <https://discord.gg/ySJD6SV>`__ where we'd be happy to hear
from you! To receive an email notification about major new releases,
send an email to `permutatriangle@gmail.com <mailto:permutatriangle@gmail.com>`_
(but please direct all requests for assistance to the
`Discord server <https://discord.gg/ySJD6SV>`__).

Installing
----------

To install ``tilings`` on your system, run:

.. code:: bash

       pip install tilings

If you would like to edit the source code, you should install ``tilings`` in
development mode by cloning the repository, running

.. code:: bash

       ./setup.py develop

To verify that your installation is correct, you can try to get a specification for
`Av(12)` by running in your terminal:

.. code:: bash

        tilescope spec 12 point_placements

You should then be all set up to use ``tilings`` and the ``TileScope`` algorithm! The
"Performance" section at the end of this document provides some more technical
information.

What are gridded permutations and tilings?
------------------------------------------

We will be brief in our definitions here, for more details see
`Christian Bean’s PhD thesis <https://opinvisindi.is/handle/20.500.11815/1184>`__.

A ``gridded permutation`` is a pair ``(π, P)`` where ``π`` is a
permutation and ``P`` is a tuple of cells, called the positions, that
denote the cells in which the points of ``π`` are drawn on a grid. Let
``G`` denote the set of all gridded permutations. Containment of gridded
permutations is defined the same as containment of permutations, except
including the preservation of the cells.

For example, ``(284376915, ((0, 0), (0, 3), (1, 1), (1, 1), (2, 3), (2, 2), (3, 4), (3, 0), (4, 2))`` is drawn on the grid as follows.

.. code:: python

       +--+--+--+--+-+
       |  |  |  |● | |
       +--+--+--+--+-+
       | ●|  |  |  | |
       |  |  |● |  | |
       +--+--+--+--+-+
       |  |  | ●|  | |
       |  |  |  |  |●|
       +--+--+--+--+-+
       |  |● |  |  | |
       |  | ●|  |  | |
       +--+--+--+--+-+
       |● |  |  |  | |
       |  |  |  | ●| |
       +--+--+--+--+-+


A ``tiling`` is a triple ``T = ((n, m), O, R)``, where ``n`` and ``m``
are positive integers, ``O`` is a set of gridded permutations called
``obstructions``, and ``R`` is a set of sets of gridded permutations
called ``requirements``.

We say a gridded permutations avoids a set of gridded permutations if it
avoids all of the permutations in the set, otherwise it contains the
set. To contain a set, therefore, means to contain at least one in the
set. The set of gridded permutations on a tiling ``Grid(T)`` is the set
of all gridded permutations in the ``n x m`` grid that avoid ``O`` and
contain each set ``r`` in ``R``.

Using tilings
-------------

Once you’ve installed ``tilings``, it can be imported by a Python script
or an interactive Python session, just like any other Python library:

.. code:: python

       >>> from tilings import *

Importing ``*`` from it supplies you with the ``GriddedPerm`` and ``Tiling``
classes.

As above, a gridded permutation is a pair ``(π, P)`` where ``π`` is a
permutation and ``P`` is a tuple of cells. The permutation is assumed to
be a ``Perm`` from the ``permuta`` Python library. Not every tuple of
cells is a valid position for a given permutation. This can be checked
using the ``contradictory`` method.

.. code:: python

       >>> from permuta import Perm
       >>> gp = GriddedPerm(Perm((0, 2, 1)), ((0, 0), (0, 0), (1, 0)))
       >>> gp.contradictory()
       False
       >>> gp = GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 1), (0, 0)))
       >>> gp.contradictory()
       True

A ``Tiling`` is created with an iterable of obstructions and an
iterable of requirements (and each requirement is an iterable of gridded permutations).
It is assumed that all cells not mentioned in some obstruction or
requirement are empty. You can print the tiling to get an overview of the
tiling created. In this example, we have a tiling that corresponds to
non-empty permutations avoiding
``123``.

.. code:: python

       >>> obstructions = [GriddedPerm.single_cell(Perm((0, 1)), (1, 1)),
       ...                 GriddedPerm.single_cell(Perm((1, 0)), (1, 1)),
       ...                 GriddedPerm.single_cell(Perm((0, 1)), (0, 0)),
       ...                 GriddedPerm.single_cell(Perm((0, 1, 2)), (2, 0)),
       ...                 GriddedPerm(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0)))]
       >>> requirements = [[GriddedPerm.single_cell(Perm((0,)), (1, 1))]]
       >>> tiling = Tiling(obstructions, requirements)
       >>> print(tiling)
       +-+-+-+
       | |●| |
       +-+-+-+
       |\| |1|
       +-+-+-+
       1: Av(012)
       \: Av(01)
       ●: point
       Crossing obstructions:
       012: (0, 0), (2, 0), (2, 0)
       Requirement 0:
       0: (1, 1)

There are several properties of ``Tiling`` that you can use, e.g.,

.. code:: python

       >>> tiling.dimensions
       (3, 2)
       >>> sorted(tiling.active_cells)
       [(0, 0), (1, 1), (2, 0)]
       >>> tiling.point_cells
       frozenset({(1, 1)})
       >>> sorted(tiling.possibly_empty)
       [(0, 0), (2, 0)]
       >>> tiling.positive_cells
       frozenset({(1, 1)})

Those who have read ahead, or already started using tilings may have noticed
that a ``Tiling`` can also be defined with a third argument called ``assumptions``.
These can be used to keep track of occurrences of gridded permutations on
tilings. These are still in development but are essential for certain
parts of the ``TileScope`` algorithm. For simplicity we will not discuss
these again until the `Fusion` section.

There are a number of methods available on the tiling. You can generate
the gridded permutations satisfying the obstructions and requirements
using the ``gridded_perms_of_length`` method.

.. code:: python

       >>> for i in range(4):
       ...     for gp in sorted(tiling.gridded_perms_of_length(i)):
       ...         print(gp)
       0: (1, 1)
       01: (0, 0), (1, 1)
       10: (1, 1), (2, 0)
       021: (0, 0), (1, 1), (2, 0)
       102: (0, 0), (0, 0), (1, 1)
       120: (0, 0), (1, 1), (2, 0)
       201: (1, 1), (2, 0), (2, 0)
       210: (1, 1), (2, 0), (2, 0)

There are numerous other methods and properties. Many of these are specific
to the ``TileScope`` algorithm, discussed in `Christian Bean’s PhD
thesis <https://opinvisindi.is/handle/20.500.11815/1184>`__. For the remainder
of this readme we will focus on the ``TileScope`` algorithm.

The TileScope algorithm
=======================


Using TileScope
---------------

If you've not installed ``tilings`` yet then go ahead and do this first by
pip installing ``tilings``:

.. code:: bash

       pip install tilings

Once done you can use the ``TileScope`` algorithm in two ways, either directly
by importing from the ``tilings.tilescope`` module which we will discuss in
greater detail shortly, or by using the ``TileScope`` command line tool.

The command line tool
---------------------

First, check the help commands for more information about its usage.

.. code:: bash

       tilescope -h
       tilescope spec -h

To search for a combinatorial specification use the subcommand
``tilescope spec``, e.g.

.. code:: bash

       tilescope spec 231 point_placements

By default this command will try to solve for the generating function,
although in some cases you will come across some not-yet-implemented features;
for more information please join us on our
`Discord server <https://discord.gg/ySJD6SV>`__, where we'd be happy to talk
about it!

The ``point_placements`` argument above is a strategy pack, which we explain in
more detail in the ``StrategyPacks`` section.

The tilescope module
--------------------
TileScope can be imported in a interactive Python session from
``tilings.tilescope``.

.. code:: python

       >>> from tilings.tilescope import *

Importing ``*`` from ``tilings.tilescope`` supplies you with the ``TileScope``
and ``TileScopePack`` classes. Running the ``TileScope`` is as simple as
choosing a class and a strategy pack. We'll go into more detail about the
different strategies
available shortly, but first let's enumerate our first permutation class. The
example one always learns first in permutation patterns is enumerating
Av(231). There are many different packs that will succeed for this class,
but to get the most commonly described decomposition we can use
``point_placements``. The basis can be given to TileScope in several
formats: an iterable of permuta.Perm, a string where the permutations
are separated by ``'_'`` (e.g. ``'231_4321'``), or as a ``Tiling``.

.. code:: python

       >>> pack = TileScopePack.point_placements()
       >>> tilescope = TileScope('231', pack)

Once we have created our ``TileScope`` we can then use the ``auto_search``
method which will search for a specification using the strategies given.
If successful it will return a CombinatorialSpecification.
``TileScope`` uses ``logzero.logger`` to report information. If you wish to
suppress these prints, you can set ``logzero.loglevel``, which we have
done here for sake of brevity in this readme!

.. code:: python

       >>> import logzero; import logging; logzero.loglevel(logging.CRITICAL)
       >>> spec = tilescope.auto_search()
       >>> print(spec)
       A combinatorial specification with 4 rules.
       -----------
       0 -> (1, 2)
       insert 0 in cell (0, 0)
       +-+            +-+     +-+
       |1|         =  | |  +  |1|
       +-+            +-+     +-+
       1: Av(120)             1: Av+(120)
                              Requirement 0:
                              0: (0, 0)
       -------
       1 -> ()
       is atom
       +-+
       | |
       +-+
       <BLANKLINE>
       -----
       2 = 3
       placing the topmost point in cell (0, 0), then row and column separation
       +-+                +-+-+-+                    +-+-+-+
       |1|             =  | |●| |                 =  | |●| |
       +-+                +-+-+-+                    +-+-+-+
       1: Av+(120)        |1| |1|                    | | |1|
       Requirement 0:     +-+-+-+                    +-+-+-+
       0: (0, 0)          1: Av(120)                 |1| | |
                          ●: point                   +-+-+-+
                          Crossing obstructions:     1: Av(120)
                          10: (0, 0), (2, 0)         ●: point
                          Requirement 0:             Requirement 0:
                          0: (1, 1)                  0: (1, 2)
       ---------
       3 -> (0,)
       tiling is locally factorable
       +-+-+-+            +-+
       | |●| |         ↝  |1|
       +-+-+-+            +-+
       | | |1|            1: Av(120)
       +-+-+-+
       |1| | |
       +-+-+-+
       1: Av(120)
       ●: point
       Requirement 0:
       0: (1, 2)

The locally factorable tiling in the rule `3 -> ()` could be further expanded
down to atoms. This can be done using the `expand_verified` method.

.. code:: python

       >>> spec.expand_verified()
       >>> print(spec)
       A combinatorial specification with 5 rules.
       -----------
       0 -> (1, 2)
       insert 0 in cell (0, 0)
       +-+            +-+     +-+
       |1|         =  | |  +  |1|
       +-+            +-+     +-+
       1: Av(120)             1: Av+(120)
                              Requirement 0:
                              0: (0, 0)
       -------
       1 -> ()
       is atom
       +-+
       | |
       +-+
       <BLANKLINE>
       -----
       2 = 3
       placing the topmost point in cell (0, 0), then row and column separation
       +-+                +-+-+-+                    +-+-+-+
       |1|             =  | |●| |                 =  | |●| |
       +-+                +-+-+-+                    +-+-+-+
       1: Av+(120)        |1| |1|                    | | |1|
       Requirement 0:     +-+-+-+                    +-+-+-+
       0: (0, 0)          1: Av(120)                 |1| | |
                          ●: point                   +-+-+-+
                          Crossing obstructions:     1: Av(120)
                          10: (0, 0), (2, 0)         ●: point
                          Requirement 0:             Requirement 0:
                          0: (1, 1)                  0: (1, 2)
       --------------
       3 -> (0, 4, 0)
       factor with partition {(0, 0)} / {(1, 2)} / {(2, 1)}
       +-+-+-+            +-+            +-+                +-+
       | |●| |         =  |1|         x  |●|             x  |1|
       +-+-+-+            +-+            +-+                +-+
       | | |1|            1: Av(120)     ●: point           1: Av(120)
       +-+-+-+                           Requirement 0:
       |1| | |                           0: (0, 0)
       +-+-+-+
       1: Av(120)
       ●: point
       Requirement 0:
       0: (1, 2)
       -------
       4 -> ()
       is atom
       +-+
       |●|
       +-+
       ●: point
       Requirement 0:
       0: (0, 0)

Now that we have a specification we can do a number of things. For example,
counting how many permutations there are in the class. This can be done using
the ``count_objects_of_size`` method on the CombinatorialSpecification.

.. code:: python

       >>> [spec.count_objects_of_size(i) for i in range(10)]
       [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]

Of course we see the Catalan numbers! We can also sample uniformly using the
``random_sample_object_of_size`` method. This will return a ``GriddedPerm``.
We have used the ``ascii_plot`` method for us to visualise it.
If you want the underlying ``Perm``, this can be accessed with the ``patt``
attribute. We also highlighted here the ``permuta.Perm.ascii_plot`` method for
an alternative visualisation.

.. code:: python

       >>> gp = spec.random_sample_object_of_size(10)
       >>> print(gp)  # doctest: +SKIP
       9543102768: (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)
       >>> print(gp.ascii_plot())  # doctest: +SKIP
       +----------+
       |●         |
       |         ●|
       |       ●  |
       |        ● |
       | ●        |
       |  ●       |
       |   ●      |
       |      ●   |
       |    ●     |
       |     ●    |
       +----------+
       >>> perm = gp.patt
       >>> print(perm)  # doctest: +SKIP
       9543102768
       >>> print(perm.ascii_plot())  # doctest: +SKIP
        | | | | | | | | | |
       -●-+-+-+-+-+-+-+-+-+-
        | | | | | | | | | |
       -+-+-+-+-+-+-+-+-+-●-
        | | | | | | | | | |
       -+-+-+-+-+-+-+-●-+-+-
        | | | | | | | | | |
       -+-+-+-+-+-+-+-+-●-+-
        | | | | | | | | | |
       -+-●-+-+-+-+-+-+-+-+-
        | | | | | | | | | |
       -+-+-●-+-+-+-+-+-+-+-
        | | | | | | | | | |
       -+-+-+-●-+-+-+-+-+-+-
        | | | | | | | | | |
       -+-+-+-+-+-+-●-+-+-+-
        | | | | | | | | | |
       -+-+-+-+-●-+-+-+-+-+-
        | | | | | | | | | |
       -+-+-+-+-+-●-+-+-+-+-
        | | | | | | | | | |


You can use the ``get_equations`` method which returns an iterator for the
system of equations implied by the specification.

.. code:: python

       >>> list(spec.get_equations())
       [Eq(F_0(x), F_1(x) + F_2(x)), Eq(F_1(x), 1), Eq(F_2(x), F_3(x)), Eq(F_3(x), F_0(x)**2*F_4(x)), Eq(F_4(x), x)]

You can also pass these directly to the ``solve`` method in ``sympy`` by using the
``get_genf`` method. It will then return the solution which matches the initial
conditions.

.. code:: python

       >>> spec.get_genf()
       (1 - sqrt(1 - 4*x))/(2*x)

The ``sympy.solve`` method can be very slow, particularly on big systems. If
you are having troubles, then other softwares such as Mathematica and Maple are
often better. You can also use the method `get_maple_equations` which will
return a string containing Maple code for the equations.

.. code:: python

       >>> print(spec.get_maple_equations())
       root_func := F[0, x]:
       eqs := [
       F[0, x] = (F[1, x] + F[2, x]),
       F[1, x] = (1),
       F[2, x] = F[3, x],
       F[3, x] = ((F[0, x]**(2)) * F[4, x]),
       F[4, x] = x
       ]:
       count := [1, 1, 2, 5, 14, 42, 132]:

If you have a system of equations you are unable to solve, then please feel
free to send them to our `Discord server <https://discord.gg/ySJD6SV>`__.

A specification can be saved and loaded later by converting it to
`JSON <https://realpython.com/python-json/>`__, a data storage format
that can be written to a file or copy-pasted elsewhere for safe keeping.
This functionality is built into `TileScope`. To retrieve the JSON representation of
a specification:

.. code:: python

       >>> import json
       >>> json.dumps(spec.to_jsonable())
       '{"root": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}, "rules": [{"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 0]]}], "requirements": [], "assumptions": []}, {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.requirement_insertion", "strategy_class": "RequirementInsertionStrategy", "ignore_parent": false, "gps": [{"patt": [0], "pos": [[0, 0]]}]}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "VerificationRule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 0]]}], "requirements": [], "assumptions": []}, "strategy": {"class_module": "tilings.strategies.verification", "strategy_class": "BasicVerificationStrategy"}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "EquivalencePathRule", "rules": [{"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[2, 1]]}, {"patt": [0, 1], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 0], "pos": [[0, 0], [2, 0]]}, {"patt": [1, 0], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 0], [2, 0], [2, 0]]}], "requirements": [[{"patt": [0], "pos": [[1, 1]]}]], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.requirement_placement", "strategy_class": "RequirementPlacementStrategy", "ignore_parent": false, "gps": [{"patt": [0], "pos": [[0, 0]]}], "indices": [0], "direction": 1, "own_col": true, "own_row": true, "include_empty": false}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[2, 1]]}, {"patt": [0, 1], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 0], "pos": [[0, 0], [2, 0]]}, {"patt": [1, 0], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 0], [2, 0], [2, 0]]}], "requirements": [[{"patt": [0], "pos": [[1, 1]]}]], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[0, 2]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[1, 1]]}, {"patt": [0], "pos": [[2, 0]]}, {"patt": [0], "pos": [[2, 2]]}, {"patt": [0, 1], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 0], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 1], [2, 1], [2, 1]]}], "requirements": [[{"patt": [0], "pos": [[1, 2]]}]], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.row_and_col_separation", "strategy_class": "RowColumnSeparationStrategy", "ignore_parent": true, "inferrable": true, "possibly_empty": false, "workable": true}}]}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[0, 2]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[1, 1]]}, {"patt": [0], "pos": [[2, 0]]}, {"patt": [0], "pos": [[2, 2]]}, {"patt": [0, 1], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 0], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 1], [2, 1], [2, 1]]}], "requirements": [[{"patt": [0], "pos": [[1, 2]]}]], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}, {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0, 1], "pos": [[0, 0], [0, 0]]}, {"patt": [1, 0], "pos": [[0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}, {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.factor", "strategy_class": "FactorStrategy", "ignore_parent": true, "workable": true, "partition": [[[0, 0]], [[1, 2]], [[2, 1]]]}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "VerificationRule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0, 1], "pos": [[0, 0], [0, 0]]}, {"patt": [1, 0], "pos": [[0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}, "strategy": {"class_module": "tilings.strategies.verification", "strategy_class": "BasicVerificationStrategy"}}]}'

To load a specification from a JSON string:

.. code:: python

       >>> json_string = '{"root": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}, "rules": [{"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 0]]}], "requirements": [], "assumptions": []}, {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.requirement_insertion", "strategy_class": "RequirementInsertionStrategy", "ignore_parent": false, "gps": [{"patt": [0], "pos": [[0, 0]]}]}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "VerificationRule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 0]]}], "requirements": [], "assumptions": []}, "strategy": {"class_module": "tilings.strategies.verification", "strategy_class": "BasicVerificationStrategy"}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "EquivalencePathRule", "rules": [{"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[2, 1]]}, {"patt": [0, 1], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 0], "pos": [[0, 0], [2, 0]]}, {"patt": [1, 0], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 0], [2, 0], [2, 0]]}], "requirements": [[{"patt": [0], "pos": [[1, 1]]}]], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.requirement_placement", "strategy_class": "RequirementPlacementStrategy", "ignore_parent": false, "gps": [{"patt": [0], "pos": [[0, 0]]}], "indices": [0], "direction": 1, "own_col": true, "own_row": true, "include_empty": false}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[2, 1]]}, {"patt": [0, 1], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 0], "pos": [[0, 0], [2, 0]]}, {"patt": [1, 0], "pos": [[1, 1], [1, 1]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 0], [2, 0], [2, 0]]}], "requirements": [[{"patt": [0], "pos": [[1, 1]]}]], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[0, 2]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[1, 1]]}, {"patt": [0], "pos": [[2, 0]]}, {"patt": [0], "pos": [[2, 2]]}, {"patt": [0, 1], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 0], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 1], [2, 1], [2, 1]]}], "requirements": [[{"patt": [0], "pos": [[1, 2]]}]], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.row_and_col_separation", "strategy_class": "RowColumnSeparationStrategy", "ignore_parent": true, "inferrable": true, "possibly_empty": false, "workable": true}}]}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "Rule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0], "pos": [[0, 1]]}, {"patt": [0], "pos": [[0, 2]]}, {"patt": [0], "pos": [[1, 0]]}, {"patt": [0], "pos": [[1, 1]]}, {"patt": [0], "pos": [[2, 0]]}, {"patt": [0], "pos": [[2, 2]]}, {"patt": [0, 1], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 0], "pos": [[1, 2], [1, 2]]}, {"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}, {"patt": [1, 2, 0], "pos": [[2, 1], [2, 1], [2, 1]]}], "requirements": [[{"patt": [0], "pos": [[1, 2]]}]], "assumptions": []}, "children": [{"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}, {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0, 1], "pos": [[0, 0], [0, 0]]}, {"patt": [1, 0], "pos": [[0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}, {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [1, 2, 0], "pos": [[0, 0], [0, 0], [0, 0]]}], "requirements": [], "assumptions": []}], "strategy": {"class_module": "tilings.strategies.factor", "strategy_class": "FactorStrategy", "ignore_parent": true, "workable": true, "partition": [[[0, 0]], [[1, 2]], [[2, 1]]]}}, {"class_module": "comb_spec_searcher.strategies.rule", "rule_class": "VerificationRule", "comb_class": {"class_module": "tilings.tiling", "comb_class": "Tiling", "obstructions": [{"patt": [0, 1], "pos": [[0, 0], [0, 0]]}, {"patt": [1, 0], "pos": [[0, 0], [0, 0]]}], "requirements": [[{"patt": [0], "pos": [[0, 0]]}]], "assumptions": []}, "strategy": {"class_module": "tilings.strategies.verification", "strategy_class": "BasicVerificationStrategy"}}]}'

       >>> from comb_spec_searcher import CombinatorialSpecification
       >>> reloaded_spec = CombinatorialSpecification.from_dict(json.loads(json_string))


StrategyPacks
=============

We have implemented a large number of structural decomposition strategies that
we will discuss a bit more in the strategies section that follows. One can use
any subset of these strategies to search for a combinatorial specification.
This can be done by creating a ``TileScopePack``.

We have prepared a number of curated packs of strategies that we find to be
rather effective. These can accessed as class methods on ``TileScopePack``.
They are:

- ``point_placements``: checks if cells are empty or not and places extreme
  points in cells
- ``row_and_col_placements``: places the left or rightmost points in columns,
  or the bottom or topmost points in rows
- ``regular_insertion_encoding``: this pack includes the strategies required
  for finding the specification corresponding to a regular insertion encoding
- ``insertion_row_and_col_placements``: this pack places rows and columns as
  above, but first ensures every active cell contains a point (this is in the
  same vein as the "slots" of the regular insertion encoding)
- ``insertion_point_placements``: places extreme points in cells, but first
  ensures every active cell contains a point
- ``pattern_placements``: inserts size one requirements into a tiling, and then
  places points with respect to a pattern, e.g. if your permutation contains 123,
  then place the leftmost point that acts as a 2 in an occurrence of 123
- ``requirement_placements``: places points with respect to any requirement,
  e.g. if your permutation contains {12, 21}, then place the rightmost point
  that is either an occurrence of 1 in 12 or an occurrence of 2 in 21.
- ``only_root_placements``: this is the same as ``pattern_placements`` except
  we only allow inserting into 1x1 tilings, therefore making it a finite pack
- ``all_the_strategies``: a pack containing (almost) all of the strategies

Each of these packs have different parameters that can be set. You can view
this by using the help command e.g.,
``help(TileScopePack.pattern_placements)``.
If you need help picking the right pack to enumerate your class join us on our
`Discord server <https://discord.gg/ySJD6SV>`__ where we'd be happy to help.

You can make any pack use the fusion strategy by using the method
``make_fusion``; for example, here is how to create the pack
``row_placements_fusion``.

.. code:: python

       >>> pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion()
       >>> print(pack)
       Looking for recursive combinatorial specification with the strategies:
       Inferral: row and column separation, obstruction transitivity
       Initial: rearrange assumptions, add assumptions, factor, tracked fusion
       Verification: verify atoms, insertion encoding verified, one by one verification, locally factorable verification
       Set 1: row placement

This particular pack can be used to enumerate ``Av(123)``.

.. code:: python

       >>> tilescope = TileScope('123', pack)
       >>> spec = tilescope.auto_search(smallest=True)
       >>> print(spec)  # doctest: +SKIP
       A combinatorial specification with 10 rules.
       -----------
       0 -> (1, 2)
       insert 0 in cell (0, 0)
       +-+            +-+     +-+
       |1|         =  | |  +  |1|
       +-+            +-+     +-+
       1: Av(012)             1: Av+(012)
                              Requirement 0:
                              0: (0, 0)
       -------
       1 -> ()
       is atom
       +-+
       | |
       +-+
       -----------
       3 -> (4, 5)
       factor with partition {(0, 0), (0, 2)} / {(1, 1)}
       +-+-+                           +-+                             +-+
       |1| |                        =  |1|                          x  |●|
       +-+-+                           +-+                             +-+
       | |●|                           |\|                             ●: point
       +-+-+                           +-+                             Requirement 0:
       |\| |                           1: Av(012)                      0: (0, 0)
       +-+-+                           \: Av(01)
       1: Av(012)                      Crossing obstructions:
       \: Av(01)                       012: (0, 0), (0, 1), (0, 1)
       ●: point
       Crossing obstructions:
       012: (0, 0), (0, 2), (0, 2)
       Requirement 0:
       0: (1, 1)
       ---------
       3 -> (5,)
       adding the assumption 'can count points in cell (0, 0)'
       +-+-+                           +-+-+
       |\|1|                        ↣  |\|1|
       +-+-+                           +-+-+
       1: Av(012)                      1: Av(012)
       \: Av(01)                       \: Av(01)
       Crossing obstructions:          Crossing obstructions:
       012: (0, 0), (1, 0), (1, 0)     012: (0, 0), (1, 0), (1, 0)
                                       Assumption 0:
                                       can count points in cell (0, 0)
       --------------
       5 -> (1, 6, 7)
       placing the topmost point in row 0
       +-+-+                               +-+     +-+-+-+                                      +-+-+-+-+
       |\|1|                            =  | |  +  |●| | |                                   +  | | |●| |
       +-+-+                               +-+     +-+-+-+                                      +-+-+-+-+
       1: Av(012)                                  | |\|1|                                      |\|\| |1|
       \: Av(01)                                   +-+-+-+                                      +-+-+-+-+
       Crossing obstructions:                      1: Av(012)                                   1: Av(012)
       012: (0, 0), (1, 0), (1, 0)                 \: Av(01)                                    \: Av(01)
       Assumption 0:                               ●: point                                     ●: point
       can count points in cell (0, 0)             Crossing obstructions:                       Crossing obstructions:
                                                   012: (1, 0), (2, 0), (2, 0)                  01: (0, 0), (1, 0)
                                                   Requirement 0:                               012: (0, 0), (3, 0), (3, 0)
                                                   0: (0, 1)                                    012: (1, 0), (3, 0), (3, 0)
                                                   Assumption 0:                                Requirement 0:
                                                   can count points in cells (0, 1), (1, 0)     0: (2, 1)
                                                                                                Assumption 0:
                                                                                                can count points in cell (0, 0)
       -----------
       6 -> (8, 5)
       factor with partition {(0, 1)} / {(1, 0), (2, 0)}
       +-+-+-+                                      +-+                                 +-+-+
       |●| | |                                   =  |●|                              x  |\|1|
       +-+-+-+                                      +-+                                 +-+-+
       | |\|1|                                      ●: point                            1: Av(012)
       +-+-+-+                                      Requirement 0:                      \: Av(01)
       1: Av(012)                                   0: (0, 0)                           Crossing obstructions:
       \: Av(01)                                    Assumption 0:                       012: (0, 0), (1, 0), (1, 0)
       ●: point                                     can count points in cell (0, 0)     Assumption 0:
       Crossing obstructions:                                                           can count points in cell (0, 0)
       012: (1, 0), (2, 0), (2, 0)
       Requirement 0:
       0: (0, 1)
       Assumption 0:
       can count points in cells (0, 1), (1, 0)
       -------
       8 -> ()
       is atom
       +-+
       |●|
       +-+
       ●: point
       Requirement 0:
       0: (0, 0)
       Assumption 0:
       can count points in cell (0, 0)
       -----------
       7 -> (9, 4)
       factor with partition {(0, 0), (1, 0), (3, 0)} / {(2, 1)}
       +-+-+-+-+                           +-+-+-+                             +-+
       | | |●| |                        =  |\|\|1|                          x  |●|
       +-+-+-+-+                           +-+-+-+                             +-+
       |\|\| |1|                           1: Av(012)                          ●: point
       +-+-+-+-+                           \: Av(01)                           Requirement 0:
       1: Av(012)                          Crossing obstructions:              0: (0, 0)
       \: Av(01)                           01: (0, 0), (1, 0)
       ●: point                            012: (0, 0), (2, 0), (2, 0)
       Crossing obstructions:              012: (1, 0), (2, 0), (2, 0)
       01: (0, 0), (1, 0)                  Assumption 0:
       012: (0, 0), (3, 0), (3, 0)         can count points in cell (0, 0)
       012: (1, 0), (3, 0), (3, 0)
       Requirement 0:
       0: (2, 1)
       Assumption 0:
       can count points in cell (0, 0)
       ---------
       9 -> (5,)
       fuse columns 0 and 1
       +-+-+-+                             +-+-+
       |\|\|1|                          ↣  |\|1|
       +-+-+-+                             +-+-+
       1: Av(012)                          1: Av(012)
       \: Av(01)                           \: Av(01)
       Crossing obstructions:              Crossing obstructions:
       01: (0, 0), (1, 0)                  012: (0, 0), (1, 0), (1, 0)
       012: (0, 0), (2, 0), (2, 0)         Assumption 0:
       012: (1, 0), (2, 0), (2, 0)         can count points in cell (0, 0)
       Assumption 0:
       can count points in cell (0, 0)
       -------
       4 -> ()
       is atom
       +-+
       |●|
       +-+
       ●: point
       Requirement 0:
       0: (0, 0)
       >>> [spec.count_objects_of_size(i) for i in range(10)]
       [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]

It is possible to make your own pack as well, but for that you should first
learn more about what the individual strategies do.

The strategies
==============

The ``TileScope`` algorithm has in essence six different strategies that are
applied in many different ways, resulting in very different universes in which
to search for a combinatorial specification in. They are:

- ``requirement insertions``: a disjoint union considering whether or not a tiling
  contains a requirement
- ``point placements``: places a uniquely defined point onto its own row and/or
  column
- ``factor``: when the obstructions and requirements become local to a set of
  cells, we factor out the local subtiling
- ``row and column separation``: if all of the points in a cell in a row must
  appear below all of the other points in the row, then separate this onto its own
  row.
- ``obstruction inferral``: add obstructions that the requirements and
  obstructions of a tiling imply must be avoided
- ``fusion``: merge two adjacent rows or columns of a tiling, if it can be
  viewed as a single row or column with a line drawn between


Requirement insertions
----------------------

The simplest of all the arguments when enumerating permutation classes is to
say, either a tiling is empty or contains a point. This can be viewed in
tilings as either avoiding ``1: (0, 0)`` or containing ``1: (0, 0)``.

.. code:: python

       >>> from tilings.strategies import CellInsertionFactory
       >>> strategy_generator = CellInsertionFactory()
       >>> tiling = Tiling.from_string('231')
       >>> for strategy in strategy_generator(tiling):
       ...     print(strategy(tiling))
       insert 0 in cell (0, 0)
       +-+            +-+     +-+
       |1|         =  | |  +  |1|
       +-+            +-+     +-+
       1: Av(120)             1: Av+(120)
                              Requirement 0:
                              0: (0, 0)

The same underlying principle corresponds to avoiding or containing any set of
gridded permutations. There are many different variations of this strategy
used throughout our ``StrategyPacks``.

.. code:: python

       >>> import tilings
       >>> print(tilings.strategies.requirement_insertion.__all__)
       ['CellInsertionFactory', 'RootInsertionFactory', 'RequirementExtensionFactory', 'RequirementInsertionFactory', 'FactorInsertionFactory', 'RequirementCorroborationFactory']

Point placements
----------------

The core idea of this strategy is to place a uniquely defined point onto
its own row and/or column. For example, here is a code snippet that
shows the rules coming from placing the extreme (rightmost, topmost, leftmost,
bottommost) points of a non-empty permutation avoiding ``231``.

.. code:: python

       >>> from tilings.strategies import PatternPlacementFactory
       >>> strategy = PatternPlacementFactory()
       >>> tiling = Tiling.from_string('231').insert_cell((0,0))
       >>> for rule in strategy(tiling):
       ...     print(rule)
       placing the rightmost point in cell (0, 0)
       +-+                +-+-+
       |1|             =  |\| |
       +-+                +-+-+
       1: Av+(120)        | |●|
       Requirement 0:     +-+-+
       0: (0, 0)          |1| |
                          +-+-+
                          1: Av(120)
                          \: Av(01)
                          ●: point
                          Crossing obstructions:
                          120: (0, 0), (0, 2), (0, 0)
                          Requirement 0:
                          0: (1, 1)
       placing the topmost point in cell (0, 0)
       +-+                +-+-+-+
       |1|             =  | |●| |
       +-+                +-+-+-+
       1: Av+(120)        |1| |1|
       Requirement 0:     +-+-+-+
       0: (0, 0)          1: Av(120)
                          ●: point
                          Crossing obstructions:
                          10: (0, 0), (2, 0)
                          Requirement 0:
                          0: (1, 1)
       placing the leftmost point in cell (0, 0)
       +-+                +-+-+
       |1|             =  | |1|
       +-+                +-+-+
       1: Av+(120)        |●| |
       Requirement 0:     +-+-+
       0: (0, 0)          | |1|
                          +-+-+
                          1: Av(120)
                          ●: point
                          Crossing obstructions:
                          10: (1, 2), (1, 0)
                          Requirement 0:
                          0: (0, 1)
       placing the bottommost point in cell (0, 0)
       +-+                +-+-+-+
       |1|             =  |\| |1|
       +-+                +-+-+-+
       1: Av+(120)        | |●| |
       Requirement 0:     +-+-+-+
       0: (0, 0)          1: Av(120)
                          \: Av(01)
                          ●: point
                          Crossing obstructions:
                          120: (0, 1), (2, 1), (2, 1)
                          Requirement 0:
                          0: (1, 0)


Other algorithms used for automatically enumerating permutation classes have
used variations of point placements. For example, enumeration schemes and the
insertion encoding essentially consider placing the bottommost point into the
row of a tiling. Here is a code snippet for calling a strategy that places
points into a row of a tiling.

.. code:: python

       >>> from permuta.misc import DIR_SOUTH
       >>> from tilings.strategies import RowAndColumnPlacementFactory
       >>> strategy = RowAndColumnPlacementFactory(place_row=True, place_col=False)
       >>> placed_tiling = tiling.place_point_in_cell((0, 0), DIR_SOUTH)
       >>> for rule in strategy(placed_tiling):
       ...     print(rule)
       placing the topmost point in row 1
       +-+-+-+                         +-+                +-+-+-+-+                       +-+-+-+-+-+
       |\| |1|                      =  |●|             +  |●| | | |                    +  | | | |●| |
       +-+-+-+                         +-+                +-+-+-+-+                       +-+-+-+-+-+
       | |●| |                         ●: point           | |\| |1|                       |\| |1| |1|
       +-+-+-+                         Requirement 0:     +-+-+-+-+                       +-+-+-+-+-+
       1: Av(120)                      0: (0, 0)          | | |●| |                       | |●| | | |
       \: Av(01)                                          +-+-+-+-+                       +-+-+-+-+-+
       ●: point                                           1: Av(120)                      1: Av(120)
       Crossing obstructions:                             \: Av(01)                       \: Av(01)
       120: (0, 1), (2, 1), (2, 1)                        ●: point                        ●: point
       Requirement 0:                                     Crossing obstructions:          Crossing obstructions:
       0: (1, 0)                                          120: (1, 1), (3, 1), (3, 1)     10: (0, 1), (4, 1)
                                                          Requirement 0:                  10: (2, 1), (4, 1)
                                                          0: (0, 2)                       120: (0, 1), (2, 1), (2, 1)
                                                          Requirement 1:                  Requirement 0:
                                                          0: (2, 0)                       0: (1, 0)
                                                                                          Requirement 1:
                                                                                          0: (3, 2)
       placing the bottommost point in row 1
       +-+-+-+                         +-+                +-+-+-+-+                       +-+-+-+-+-+
       |\| |1|                      =  |●|             +  |\| | |1|                    +  |\| |\| |1|
       +-+-+-+                         +-+                +-+-+-+-+                       +-+-+-+-+-+
       | |●| |                         ●: point           | |●| | |                       | | | |●| |
       +-+-+-+                         Requirement 0:     +-+-+-+-+                       +-+-+-+-+-+
       1: Av(120)                      0: (0, 0)          | | |●| |                       | |●| | | |
       \: Av(01)                                          +-+-+-+-+                       +-+-+-+-+-+
       ●: point                                           1: Av(120)                      1: Av(120)
       Crossing obstructions:                             \: Av(01)                       \: Av(01)
       120: (0, 1), (2, 1), (2, 1)                        ●: point                        ●: point
       Requirement 0:                                     Crossing obstructions:          Crossing obstructions:
       0: (1, 0)                                          120: (0, 2), (3, 2), (3, 2)     01: (0, 2), (2, 2)
                                                          Requirement 0:                  120: (0, 2), (4, 2), (4, 2)
                                                          0: (1, 1)                       120: (2, 2), (4, 2), (4, 2)
                                                          Requirement 1:                  Requirement 0:
                                                          0: (2, 0)                       0: (1, 0)
                                                                                          Requirement 1:
                                                                                          0: (3, 1)



Row and column separation
-------------------------

Every non-empty permutation in ``Av(231)`` can be written in the form αnβ where
``α``, ``β`` are permutation avoiding ``231``, and all of the values in ``α``
are below all of the values in ``β``. The tiling representing placing the
topmost point in ``Av(231)`` contains a crossing size 2 obstruction
``10: (0, 0), (2, 0)``. This obstruction precisely says that the points in the
cell ``(0, 0)`` must appear below the points in the cell ``(2, 0)``. The
``RowColumnSeparationStrategy`` will try to separate the rows and columns as
much as possible according to the size two crossing obstructions.

.. code:: python

       >>> from permuta.misc import DIR_NORTH
       >>> from tilings.strategies import RowColumnSeparationStrategy
       >>> strategy = RowColumnSeparationStrategy()
       >>> placed_tiling = tiling.place_point_in_cell((0, 0), DIR_NORTH)
       >>> rule = strategy(placed_tiling)
       >>> print(rule)
       row and column separation
       +-+-+-+                    +-+-+-+
       | |●| |                 =  | |●| |
       +-+-+-+                    +-+-+-+
       |1| |1|                    | | |1|
       +-+-+-+                    +-+-+-+
       1: Av(120)                 |1| | |
       ●: point                   +-+-+-+
       Crossing obstructions:     1: Av(120)
       10: (0, 0), (2, 0)         ●: point
       Requirement 0:             Requirement 0:
       0: (1, 1)                  0: (1, 2)


Factor
------

If there are no crossing obstructions between two cells ``a`` and ``b`` on a
tiling then the choice of points in ``a`` are independent from the choice
of points in ``b``.

.. code:: python

       >>> separated_tiling = rule.children[0]
       >>> from tilings.strategies import FactorFactory
       >>> strategy_generator = FactorFactory()
       >>> for strategy in strategy_generator(separated_tiling):
       ...     print(strategy(separated_tiling))
       factor with partition {(0, 0)} / {(1, 2)} / {(2, 1)}
       +-+-+-+            +-+            +-+                +-+
       | |●| |         =  |1|         x  |●|             x  |1|
       +-+-+-+            +-+            +-+                +-+
       | | |1|            1: Av(120)     ●: point           1: Av(120)
       +-+-+-+                           Requirement 0:
       |1| | |                           0: (0, 0)
       +-+-+-+
       1: Av(120)
       ●: point
       Requirement 0:
       0: (1, 2)

The ``x`` in the printed above rule is used to denote Cartesian product.
We do this to signify that there is a size-preserving bijection between the
gridded permutations on the left-hand side, to the set of 3-tuples coming from
the Cartesian product on the right-hand side, where the size of a tuple is the
sum of the sizes of the parts. In particular, it implies that the enumeration
of the gridded permutations on the left-hand side can be computed by applying the
Cauchy product to the enumerations of the three sets of gridded permutations on
the right-hand side.

To guarantee that these rules are always counted using the Cauchy product
we must also ensure any two cells on the same row or column are also contained
in the same factor, otherwise when counting the left-hand side we have to
consider the possible interleavings going on.

.. code:: python

       >>> tiling = Tiling.from_string('231_132').insert_cell((0,0))
       >>> placed_tiling = tiling.place_point_in_cell((0, 0), DIR_SOUTH)
       >>> strategy_generator = FactorFactory()
       >>> for strategy in strategy_generator(placed_tiling):
       ...     print(strategy(placed_tiling))
       factor with partition {(0, 1), (2, 1)} / {(1, 0)}
       +-+-+-+            +-+-+         +-+
       |\| |/|         =  |\|/|      x  |●|
       +-+-+-+            +-+-+         +-+
       | |●| |            /: Av(10)     ●: point
       +-+-+-+            \: Av(01)     Requirement 0:
       /: Av(10)                        0: (0, 0)
       \: Av(01)
       ●: point
       Requirement 0:
       0: (1, 0)

Using the setting ``all`` in ``FactorFactory`` will allow us to factor
according to only the obstructions and requirements.

.. code:: python

       >>> strategy_generator = FactorFactory('all')
       >>> for strategy in strategy_generator(placed_tiling):
       ...     print(strategy(placed_tiling))
       interleaving factor with partition {(0, 1)} / {(1, 0)} / {(2, 1)}
       +-+-+-+            +-+           +-+                +-+
       |\| |/|         =  |\|        *  |●|             *  |/|
       +-+-+-+            +-+           +-+                +-+
       | |●| |            \: Av(01)     ●: point           /: Av(10)
       +-+-+-+                          Requirement 0:
       /: Av(10)                        0: (0, 0)
       \: Av(01)
       ●: point
       Requirement 0:
       0: (1, 0)

We instead use the symbol ``*`` to make us aware that this is not counted
by the Cauchy product, but we must also count the possible interleavings.


Obstruction inferral
--------------------

The presence of requirements alongside the obstructions on a tiling can
sometimes be used to imply that all of the gridded permutations on a tiling also avoid
some additional obstruction. The goal of ``ObstructionInferral`` is to add these to
a tiling.

.. code:: python

       >>> from permuta.misc import DIR_NORTH
       >>> tiling = Tiling.from_string('1234_1243_1423_4123')
       >>> placed_tiling = tiling.partial_place_point_in_cell((0, 0), DIR_NORTH)
       >>> from tilings.strategies import ObstructionInferralFactory
       >>> strategy_generator = ObstructionInferralFactory(3)
       >>> for strategy in strategy_generator(placed_tiling):
       ...     print(strategy(placed_tiling))
       added the obstructions {012: (0, 0), (0, 0), (0, 0)}
       +-+                                      +-+
       |●|                                   =  |●|
       +-+                                      +-+
       |1|                                      |1|
       +-+                                      +-+
       1: Av(0123, 0132, 0312, 3012)            1: Av(012)
       ●: point                                 ●: point
       Crossing obstructions:                   Requirement 0:
       0123: (0, 0), (0, 0), (0, 0), (0, 1)     0: (0, 1)
       0132: (0, 0), (0, 0), (0, 1), (0, 0)
       0312: (0, 0), (0, 1), (0, 0), (0, 0)
       3012: (0, 1), (0, 0), (0, 0), (0, 0)
       Requirement 0:
       0: (0, 1)

In the above code snippet, we have added the obstruction
``gp = 012: (0, 0), (0, 0), (0, 0)``. In particular, the 4 crossing
obstructions, and the 4 localised obstructions, all contained a copy of ``gp``,
so we simplify the right-hand side by removing these from the tiling.
This simplification step happens automatically when creating a ``Tiling``.

Fusion
------

Consider the gridded permutations on the following tiling.

.. code:: python

       >>> tiling = Tiling([GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))), GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))), GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0)))])
       >>> print(tiling)
       +-+-+
       |\|\|
       +-+-+
       \: Av(01)
       Crossing obstructions:
       01: (0, 0), (1, 0)
       >>> for i in range(4):
       ...     for gp in sorted(tiling.gridded_perms_of_length(i)):
       ...         print(gp)
       ε:
       0: (0, 0)
       0: (1, 0)
       10: (0, 0), (0, 0)
       10: (0, 0), (1, 0)
       10: (1, 0), (1, 0)
       210: (0, 0), (0, 0), (0, 0)
       210: (0, 0), (0, 0), (1, 0)
       210: (0, 0), (1, 0), (1, 0)
       210: (1, 0), (1, 0), (1, 0)

Due to the crossing ``01`` obstruction it is clear that all of the underlying
permutations will be decreasing. Moreover, the transition between the left cell
and the right cell can be between any of the points. In particular, this says
there are ``n + 1`` gridded permutations of size ``n`` on this tiling. We
capture this idea by fusing the two columns into a single column.

.. code:: python

       >>> from tilings.strategies import FusionFactory
       >>> strategy_generator = FusionFactory()
       >>> for rule in strategy_generator(tiling):
       ...     print(rule)
       fuse columns 0 and 1
       +-+-+                      +-+
       |\|\|                   ↣  |\|
       +-+-+                      +-+
       \: Av(01)                  \: Av(01)
       Crossing obstructions:     Assumption 0:
       01: (0, 0), (1, 0)         can count points in cell (0, 0)

We use the symbol ``↣`` instead of ``=`` to remind us that the counts of the
two sides are definitely not the same.
Notice, the right-hand side tiling here also now requires that we can count the
number of points in cell ``(0, 0)``. If there are ``k`` points in cell ``(0, 0)``
in a gridded permutation then there will be ``k + 1`` gridded permutations that
fuse to this gridded permutation. Of course, here the number of points in cell``(0, 0)``
is going to be equal to the size of the gridded permutation, but in general,
the points that need to be counted might not cover the whole tiling. For
example, the following rule was used within specification to enumerate
``Av(123)``.

.. code:: python

       >>> tiling = Tiling(
       ...     [
       ...         GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
       ...         GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
       ...         GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
       ...         GriddedPerm(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
       ...         GriddedPerm(Perm((0, 1, 2)), ((1, 0), (2, 0), (2, 0))),
       ...         GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
       ...     ]
       ... )
       >>> for rule in strategy_generator(tiling):
       ...     print(rule)
       fuse columns 0 and 1
       +-+-+-+                         +-+-+
       |\|\|1|                      ↣  |\|1|
       +-+-+-+                         +-+-+
       1: Av(012)                      1: Av(012)
       \: Av(01)                       \: Av(01)
       Crossing obstructions:          Crossing obstructions:
       01: (0, 0), (1, 0)              012: (0, 0), (1, 0), (1, 0)
       012: (0, 0), (2, 0), (2, 0)     Assumption 0:
       012: (1, 0), (2, 0), (2, 0)     can count points in cell (0, 0)

Performance
-----------
The `TileScope` algorithm can be resource-intensive in both time and memory. This
codebase is fully compatible with `PyPy <https://www.pypy.org/>`__, an alternative
Python interpreter that usually runs `TileScope` 5x - 7x faster, at the cost of higher
memory usage (sometimes as high as 2x). This extra memory usage is largely caused by
PyPy's approach to incremental garbage collection, and as a result can be partially
mitigated by setting the environmental variables
`described here <https://doc.pypy.org/en/latest/gc_info.html#environment-variables>`__.
For example, the configuration

.. code::

    PYPY_GC_MAJOR_COLLECT=1.1
    PYPY_GC_MAX_DELTA=200MB
    PYPY_GC_INCREMENT_STEP=10GB

tends to improve memory usage at the cost of 30% - 50% extra time.

If memory usage, rather than time usage, is a bottleneck, then the default interpreter
``CPython`` is preferred.

=========

Finally, we'd like to reiterate, if you need support, have a suggestion, or just
want to be up to date with the latest developments please join us on our
`Discord server <https://discord.gg/ySJD6SV>`__ where we'd be happy to hear
from you!
