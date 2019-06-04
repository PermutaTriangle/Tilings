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


``tilings`` is a Python library for working with gridded permutation and
tilings.

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

Importing ``*`` from it supplies you with the ‘GriddedPerm’,
‘Obstruction’, ‘Requirement’, and ‘Tiling’ classes.

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

A ``Tiling`` is created with an iterable of ``Obstruction`` and an
iterable of ``Requirement`` lists. It is assumed that all cells not
mentioned in some obstruction or requirement is empty. You can print the
tiling to get an overview of the tiling created. In this example, we
have a tiling that corresponds to non-empty permutation avoiding
``123``.

.. code:: python

       >>> obstructions = [Obstruction.single_cell(Perm((0, 1)), (1, 1)),
       ...                 Obstruction.single_cell(Perm((1, 0)), (1, 1)),
       ...                 Obstruction.single_cell(Perm((0, 1)), (0, 0)),
       ...                 Obstruction.single_cell(Perm((0, 1, 2)), (2, 0)),
       ...                 Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0)))]
       >>> requirements = [[Requirement.single_cell(Perm((0,)), (1, 1))]]
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

There are a number of methods available on the tiling. You can generate
the gridded permutations satisfying the obtructions and requirements
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
