(unreleased)
------------

New
~~~
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
- add hooks:
    qml_context_property
    qml_applicationAvailable
    qml_qmlEngineAvalaible
- add qmlRegisterType support
