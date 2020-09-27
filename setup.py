#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages

from src.pytestqml import __version__


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-qml",
    version=__version__,
    author="Jimmy Girardet",
    author_email="ijkl@netc.fr",
    maintainer="Jimmy Girardet",
    maintainer_email="ijkl@netc.fr",
    license="GNU GPL v3.0",
    url="https://github.com/jgirardet/pytest-qml",
    description="Run QML Tests with pytest",
    long_description=read("README.md"),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"pytest11": ["pytest-qml = pytestqml.plugin"]},
    # py_modules=['pytest_pytestqml'],
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["pytest>=6.0.0", "termcolor"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    # entry_points={
    #     'pytest11': [
    #         'qml = pytest_pytestqml',
    #     ],
    # },
)
