#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="grids_three",
    version="0.1.0",
    author="Henning Ulfarsson",
    author_email="henningu@ru.is",
    maintainer="Christian Nathaniel Bean",
    maintainer_email="christianbean@ru.is",
    url="https://github.com/PermutaTriangle/grids_three",
    packages=find_packages(),
    long_description=read("README.md"),
    install_requires=['permuta'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest',
                   'permuta',
                   'pytest-pep8',
                   'pytest-isort']
)
