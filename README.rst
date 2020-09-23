==========
pytest-qml
==========

.. image:: https://img.shields.io/pypi/v/pytest-qml.svg
    :target: https://pypi.org/project/pytest-qml
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-qml.svg
    :target: https://pypi.org/project/pytest-qml
    :alt: Python versions

.. image:: https://travis-ci.org/jgirardet/pytest-qml.svg?branch=master
    :target: https://travis-ci.org/jgirardet/pytest-qml
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/jgirardet/pytest-qml?branch=master
    :target: https://ci.appveyor.com/project/jgirardet/pytest-qml/branch/master
    :alt: See Build Status on AppVeyor

Run QML Tests with pytest

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* TODO


Requirements
------------

* TODO


Installation
------------

You can install "pytest-qml" via `pip`_ from `PyPI`_::

    $ pip install pytest-qml


Usage
-----

* TODO

Differences with C++ implementation
--------------------------------------
pytest-qml aimns to be fully compatible with QML QtTest public api except importing `import PyTest 1.0` instead
of `import QtTest 1.2`.
Were are actually trying to make it pass QtTest test suite. You can follow it here https://github.com/jgirardet/pytest-qml/issues/2.


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `GNU GPL v3.0`_ license, "pytest-qml" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/jgirardet/pytest-qml/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
