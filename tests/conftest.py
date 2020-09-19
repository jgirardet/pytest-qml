from string import Template

import pytest

pytest_plugins = "pytester"



BASE1CAS1TEST = Template(
    """
import QtQuick 2.14
import PythonTestCase 1.0
Item {
    TestCase {
        id: testcase
        name: "TestBla"
        function test_fonction() {
            ${fn}
        }
    }
}
"""
)

GABARIT = Template(
    """
import QtQuick 2.14
import PythonTestCase 1.0
Item {
    ${content}
}
"""
)

@pytest.fixture
def file1cas1test1(testdir):
    def wrapped(fn,  *args, run=True):
        testdir.makefile(
            ".qml",
            tst_BBB=BASE1CAS1TEST.substitute(fn=fn),
        )
        if run:
            result = testdir.runpytest("-s", *args)
        return testdir, result

    return wrapped

@pytest.fixture
def gabarit(testdir, run=True):
    def wrapped(content):
        testdir.makefile(
            ".qml",
            tst_BBB=GABARIT.substitute(content=content),
        )
        if run:
            result = testdir.runpytest("-s")
        return testdir, result

    return wrapped