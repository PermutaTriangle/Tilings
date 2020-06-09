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
permutations and tilings, and in particular the ``tilescope`` algorithm which
can be used to enumerate permutation classes.

If you are primarily interested in enumerating permutation classes, then you
may wish to skip ahead to the ``tilescope`` section, but note the installation
will be the same as for ``tilings``.

If you need support, have a suggestion, or just want to be up to date with the
latest developments please join us on our
`Discord server <https://discord.gg/ySJD6SV>`__ where we'd be happy to hear
from you!

Installing
----------

To install ``tilings`` on your system, run:

.. code:: bash

       pip install tilings

It is also possible to install ``tilings`` in development mode to work
on the source code, in which case you run the following after cloning
the repository:

.. code:: bash

       ./setup.py develop

To run the unit tests:

.. code:: bash

       ./setup.py test

You should be all set up to use ``tilings`` and the ``tilescope`` algorithm!

What are gridded permutations and tilings?
------------------------------------------

We will be brief in our definitions here, for more details see
`Christian Bean’s PhD thesis <https://skemman.is/handle/1946/31663>`__.

A ``gridded permutation`` is a pair ``(π, P)`` where ``π`` is a
permutation and ``P`` is a tuple of cells, called the positions, that
denote the cells in which the points of ``π`` are drawn on a grid. Let
``G`` denote the set of all gridded permutations. Containment of gridded
permutations is defined the same as containment of permutations, except
including the preservation of the cells.

A ``tiling`` is a triple ``T = ((n, m), O, R)``, where ``n`` and ``m``
are positive integers, ``O`` is a set of gridded permutations called
``obstructions``, and ``R`` is a set of sets of gridded permutations
called ``requirements``.

We say a gridded permutations avoids a set of gridded permutations if it
avoids all of the permutations in the set, otherwise it contains the
set. To contain a set, therefore, means contains at least one in the
set. The set of gridded permutations on a tiling ``Grid(T)`` is the set
of all gridded permutations in the ``n x m`` grid that avoids ``O`` and
contains each set ``r`` in ``R``.

Using tilings
-------------

Once you’ve installed ``tilings``, it can be imported by a Python script
or an interactive Python session, just like any other Python library:

.. code:: python

       >>> from tilings import *

Importing ``*`` from it supplies you with the ‘GriddedPerm’ and ‘Tiling’
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

A ``Tiling`` is created with an iterable of obstruction and an
iterable of requirement lists. It is assumed that all cells not
mentioned in some obstruction or requirement is empty. You can print the
tiling to get an overview of the tiling created. In this example, we
have a tiling that corresponds to non-empty permutation avoiding
``123``.

.. code:: python

       >>> obstructions = [GriddedPerm.single_cell(Perm((0, 1)), (1, 1)),
       ...                 GriddedPerm.single_cell(Perm((1, 0)), (1, 1)),
       ...                 GriddedPerm.single_cell(Perm((0, 1)), (0, 0)),
       ...                 GriddedPerm.single_cell(Perm((0, 1, 2)), (2, 0)),
       ...                 GriddedPerm(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0)))]
       >>> requirements = [[GriddedPerm.single_cell(Perm((0,)), (1, 1))]]
       >>> til = Tiling(obstructions, requirements)
       >>> print(til)
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
       >>> til.dimensions
       (3, 2)
       >>> sorted(til.active_cells)
       [(0, 0), (1, 1), (2, 0)]
       >>> til.point_cells
       frozenset({(1, 1)})
       >>> sorted(til.possibly_empty)
       [(0, 0), (2, 0)]
       >>> til.positive_cells
       frozenset({(1, 1)})

A keen reader may have observed that a tiling can also take a third argument
called assumptions. These can be used to keep track of occurrences gridded
permutations on tilings. These are still in development mode but are essential
for certain parts of the tilescope algorithm. For simplicity we will not
discuss these again until the `Fusion` section.

There are a number of methods available on the tiling. You can generate
the gridded permutations satisfying the obstructions and requirements
using the ``gridded_perms_of_length`` method.

.. code:: python

       >>> for i in range(4):
       ...     for gp in til.gridded_perms_of_length(i):
       ...         print(gp)
       0: (1, 1)
       10: (1, 1), (2, 0)
       01: (0, 0), (1, 1)
       210: (1, 1), (2, 0), (2, 0)
       201: (1, 1), (2, 0), (2, 0)
       120: (0, 0), (1, 1), (2, 0)
       021: (0, 0), (1, 1), (2, 0)
       102: (0, 0), (0, 0), (1, 1)

There are numerous other methods and properties. Many of these specific
to the ``tilescope`` algorithm, discussed in `Christian Bean’s PhD
thesis <https://skemman.is/handle/1946/31663>`__.

The TileScope algorithm
=======================



Using the tilescope
-------------------

If you've not installed ``tilings`` yet then go ahead and do this first.
Then TileScope can be imported in a interactive Python session
from ``tilings.tilescope``.

.. code:: python

       >>> from tilings.tilescope import *

Importing ``*`` from ``tilings.tilescope`` supplies you with the "TileScope" and
‘TileScopePack’ classes. Running the TileScope is as simple as choosing a class
and a strategy pack. We'll go into more detail about the different strategies
available shortly, but first lets enumerate our first permutation class. The
example one always learns first in permutation patterns is enumerating Av(231).
There are many different packs that will succeed for this class, but to get the
most commonly described decomposition we can use ``point_placements``. The
basis can be given to TileScope in several formats: an iterable of permuta.Perm,
a string where the permutations are separated by ``'_'`` (e.g. ``'231_4321'``, or
as a ``Tiling``.

.. code:: python

       >>> pack = TileScopePack.point_placements()
       >>> tilescope = TileScope('231', pack)

Once we have created our ``TileScope`` we can then use the ``auto_search`` method
which will search for a specification using the strategies given. If successful
it will return a CombinatorialSpecification.
``TileScope`` uses ``logzero.logger`` to report information. If you wish to
surpress these prints, you can set ``logzero.loglevel``, which I have done here
for sake of brevity in this readme!

.. code:: python

       >>> import logzero; import logging; logzero.loglevel(logging.CRITICAL)
       >>> spec = tilescope.auto_search()
       >>> print(spec)
       A combinatorial specification with 5 rules.

       0 -> (1, 2)
       Explanation: insert 0 in cell (0, 0)
       +-+            +-+     +-+
       |1|         =  | |  +  |1|
       +-+            +-+     +-+
       1: Av(120)             1: Av+(120)
                            Requirement 0:
                            0: (0, 0)

       1 -> ()
       Explanation: is atom
       +-+
       | |
       +-+


       2 = 3
       Explanation: placing the topmost point in cell (0, 0), then row and column separation
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

       3 -> (0, 4, 0)
       Explanation: factor with partition {(0, 0)} / {(1, 2)} / {(2, 1)}
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

       4 -> ()
       Explanation: is atom
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
``random_sample_object_of_size`` method. This will return a gridded perm. If you
just want the underlying perm, this can be accessed with ``patt`` attribute.
I have done this here, and then used the ``permuta.Perm.ascii_plot`` method for
us to visualise it.

.. code:: python

       >>> gp = spec.random_sample_object_of_size(10)
       >>> perm = gp.patt
       >>> print(perm)
       5042136987
       >>> print(perm.ascii_plot())
       | | | | | | | | | |
       -+-+-+-+-+-+-+-●-+-+-
       | | | | | | | | | |
       -+-+-+-+-+-+-+-+-●-+-
       | | | | | | | | | |
       -+-+-+-+-+-+-+-+-+-●-
       | | | | | | | | | |
       -+-+-+-+-+-+-●-+-+-+-
       | | | | | | | | | |
       -●-+-+-+-+-+-+-+-+-+-
       | | | | | | | | | |
       -+-+-●-+-+-+-+-+-+-+-
       | | | | | | | | | |
       -+-+-+-+-+-●-+-+-+-+-
       | | | | | | | | | |
       -+-+-+-●-+-+-+-+-+-+-
       | | | | | | | | | |
       -+-+-+-+-●-+-+-+-+-+-
       | | | | | | | | | |
       -+-●-+-+-+-+-+-+-+-+-
       | | | | | | | | | |


You might be interested in righting the system of equations. You can use the
``get_equations`` which returns an iterator of the equations.

.. code:: python

       >>> list(spec.get_equations())
       [Eq(F_0(x), F_1(x) + F_2(x)), Eq(F_1(x), 1), Eq(F_2(x), F_3(x)), Eq(F_3(x), F_0(x)**2*F_4(x)), Eq(F_4(x), x)]

You can also pass these directly to the ``solve`` method in ``sympy`` by using the
``get_genf`` method.

.. code:: python

       >>> spec.get_genf()
       -sqrt(1 - 4*x)/(2*x) + 1/(2*x)


Using the fusion strategy
-------------------------




Finally, I'd like reiterate, if you need support, have a suggestion, or just
want to be up to date with the latest developments please join us on our
`Discord server <https://discord.gg/ySJD6SV>`__ where we'd be happy to hear
from you!
