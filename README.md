# pytest-qml

![build](https://github.com/jgirardet/pytest-qml/workflows/build/badge.svg?branch=master)
![pypi](https://img.shields.io/pypi/v/pytest-qml.svg)
![downloads](https://static.pepy.tech/badge/pytest-qml)

## Run QML Tests with PyTest

## Features
This pytest plugin allows you to run qml tests via pytest 
instead of the C++/QtQuick test runner. It supports both PySide2 and PyQt5 >= 5.14.2 .


## Installation
```shell
pip install pytest-qml
```
## Usage
Pytest-qml aims to be fully compatible with [Qt Quick Test](https://doc.qt.io/qt-5/qtquicktest-index.html#executing-c-before-qml-tests) public api except using a 
custom `TestCase` importing `import PyTest 1.0` instead of `import QtTest 1.2`.
We  are aiming  to make it pass QtTest test suite. You can follow it at [issue 2](https://github.com/jgirardet/pytest-qml/issues/2).
Already implemented Features, properties and methods can be found at [issue 1](https://github.com/jgirardet/pytest-qml/issues/1).

```qml
import QtQuick 2.0
import PyTest 1.0

Item {
    TestCase {
        function test_something() {
            compare(1,1)
        }                                               
    }                            
}
```

Run pytest. PyTest will collect tests in folder and subfolders like other python tests.
```shell
pytest
```
You can tell PyTest to not run qml tests with the option `--skip-qml`.
```shell
pytest --skip-qml
```
Qml logging is shutdown by default since it uses `pytest-qt` under the hood which captures all qt/qml logging by default.
To see qml logs add `--no-qt-log` to pytest's `-s` option. More info at [pytest-qt](https://pytest-qt.readthedocs.io/en/latest/logging.html)
```shell
pytest -s --no-qt-log
```

## Executing Python code before QML Tests

This is done using [pytest's hook system](https://docs.pytest.org/en/stable/writing_plugins.html#writing-hook-functions).
Pytest-qml add's the following custom hooks:
 
### pytest_qml_applicationAvalaible
Same thing like C++ `applicationAvaliable`, except an `app` parameter provided for convenience.

```python
# conftest.py
def pytest_qml_applicationAvailable(app):
    app.setApplicationName("Cool App")
```

### pytest_qml_qmlEngineAvalaible
Same thing like C++ `qmlEngineAvailable`.

```python
def pytest_qml_qmlEngineAvailable(engine):
        engine.addImportPath("/some/path")
```
##### about setting a ContextProperty
Objects added with `engine.rootContext.setContextProperty("name", obj)` need to 
stay referenced somewhere and not be garbage collected. The following code will
not work:
```python
# conftest.py
def pytest_qml_qmlEngineAvailable(engine):
        engine.rootContext().setContextProperty("name", SomeObject())
        # ====> fail:  SomeObject() is garbage collected    
        
```
To accomplish it there are various poosiblities:
  - Instantiate the object inside `conftest.py` file, it will exist during the whole test session:
```python
# conftest.py
obj = SomeObj()
def pytest_qml_qmlEngineAvailable(engine):
        engine.rootContext().setContextProperty("name", obj)
```
  - add the object as attribute of engine, it will exists for the whole test file:
```python
#conftest.py
def pytest_qml_qmlEngineAvailable(engine):
        engine.cp = SomeObject()
        engine.rootContext().setContextProperty("name", engine.cp)
        
```
  - use the hook  [pytest_qml_context_properties](pytest_qml_context_properties)



### pytest_qml_context_properties
This a convenience hook to register contextProperties. ContextProperty  will exist for the
whole test file. It takes no parameter and returns a dict.
```python
# contest.py
def pytest_qml_context_properties():
        return {"cp":Cp()}
```

### Resistering new types
This can be done inside `conftest.py` or in the `pytest_configure` hook:
```python
# conftest.py

qmlRegisterType(MyObj, "MyType", 1, 0, "MyObj")

# or inside the hook
def pytest_configure():
    qmlRegisterType(MyObj, "MyType", 1, 0, "MyObj")

```

### Using Qt .qrc file
This can be done inside `conftest.py` or in the `pytest_sessionstart` hook:
```python
# conftest.py

from package import ressources.qrc

# or inside the hook
def pytest_sessionstart():
    from package import ressources.qrc
```

## Issues

If you encounter any problems, please [fille an issue](https://github.com/jgirardet/pytest-qml/issues/new/choose) along with a detailed description.
    

## Contributing
Every contribution is always welcomed. Don't hesitate to ask for some
help if you need it, I'll be happy to provide some guidance.
A good start is to look at  [issue 1](https://github.com/jgirardet/pytest-qml/issues/1)
to see what  still need to be done.

- clone the repo and go inside
```shell
git clone https://github.com/jgirardet/pytest-qml
cd pytest-qml
```
-  create a virtual env and activate it
```shell
python3 -m venv myenv
source myenv/bin/activate
```
- update pip and install requirements
```shell
pip install -U pip
pip install -r requirements.txt
```
- install pre-commit hook (we use black)
```shell
pre-commit install
```
- make your changes
- add your name to contributor
- Commit and push a Pull request

## License


Distributed under the terms of the `GNU GPL v3.0` license, "pytest-qml" is free and open source software.
Code parts from PySide2 owning to Qt Company are licensed under the `LGPL-3.0`.

## Contributors
Thanks to all the contributors helping in this project.
- Jimmy Girardet
- coming... hopefully :-)

## Changelog
#### 0.3.0
- New
    - use Custom TestCase
    - use Pytest
        - option --skip-qml
        - nice qml error report
    - use custom TestCase from module PyTest 1.0
        - findChild, createTemporaryObject
        - expectFail, fail, skip
        - keySequence, keyClick, keyPress, keyRelease.
        - tryVerify, verify, compare, tryCompare
        - mousePress, mouseMove, mouseClick, mouseDClick.
        - init, cleanup, initTestCase, cleanuptestCase
    - add hooks : qml_context_property, qml_applicationAvailable, qml_qmlEngineAvalaible
    - add qmlRegisterType support

