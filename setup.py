#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="tilings",
    version=get_version("tilings/__init__.py"),
    author="Permuta Triangle",
    author_email="permutatriangle@gmail.com",
    description="A Python library for gridded permutations and tilings.",
    license="BSD-3",
    keywords=(
        "permutation perm gridded pattern tiling avoid contain" "occurrences grid class"
    ),
    url="https://github.com/PermutaTriangle/Tilings",
    project_urls={
        "Source": "https://github.com/PermutaTriangle/Tilings",
        "Tracker": "https://github.com/PermutaTriangle/Tilings/issues",
    },
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=read("README.rst"),
    install_requires=[
        "comb-spec-searcher==3.0.0",
        "permuta==2.0.2",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    entry_points={"console_scripts": ["tilescope=tilings.cli:main"]},
)
