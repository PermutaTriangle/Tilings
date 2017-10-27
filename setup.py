#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="grids_two",
    version="0.0.1",
    author="Henning Ulfarsson",
    author_email="henningu@ru.is",
    url="https://github.com/PermutaTriangle/grids_two",
    packages=find_packages(),
    long_description=read("README.md"),
    dependency_links=[
        'git+https://github.com/PermutaTriangle/Permuta#egg=permuta-0.0.1',
        'git+https://github.com/PermutaTriangle/grids#egg=grids-0.0.1'],
    install_requires=['permuta',
                      'grids'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest',
                   'permuta',
                   'pytest-pep8',
                   'pytest-isort']
)
