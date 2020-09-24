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
    - init, cleanup
- add context_property support
- add qmlRegisterType support

Changes
~~~~~~~
- Chor: add black and pre-commit.
- Chor: add pre-commit.

Fix
~~~
- Bug: fix report on non PytestError.
- Bug: fix tryVerify to compare true to boolean.
- Bug: use attr instead of  dataclass for python 3.6 compatibily. [Jimmy
  Girardet]
- Refactor: use lodash.isEqual in compare et test tst_compare.qml from
  QtTest suite.
- Refactor: move classes to node.
- Refactor: PythonTestCase -> Pytest.

CI/Tests
~~~~~~~~
- Ci: maybe..
- Ci: windows enconding error ....
- Ci: unlock yml deploy.
- Ci: fix windows encoding.
- Ci:remove a "-s" parameter for character enconding on windows. [Jimmy
  Girardet]
- Test: add runalone marker for some tests needed to be run alone.

- Tests: fix in tox.
- Ci: try fix keyboard on linux.
- Ci: try fix keyboard on linux.
- Ci: try fix keyboard on linux.
- Test: exclude projec from tox.
- Test: remove qmlbot.wait(0), failing to much.
- Ci: test_windowsshown.
- Ci: env linux.
- Ci: display.
- Ci: test ci v exposed bot shown.
- Ci: test ci v exposed bot shown.
- Ci: test ci v exposed bot shown.
- Ci: test ci v exposed.
- Ci: test ci fail without qmlbot.
- Ci: test ci fail.
- Ci: add windowShown.
- Ci: remove python39.
- Ci: python39.
- Ci: python39.
- Ci: python39.
- Ci: python39.
- Ci: python39.
- Ci: tweak wait for mac os.
- Ci: disbla windosshown.
- Ci: pytet verbose.
- Ci: QT_QPA_PLATFORM=offscreen.
- Ci: add many platforms.
- Ci: add many platforms.

Other
~~~~~
- Style: nice error report.
- Style: black.
- Initial.


