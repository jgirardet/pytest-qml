from string import Template

import pytest

pytest_plugins = "pytester"


BASE1CAS1TEST = Template(
    """
import QtQuick 2.14
import QtQuick.Controls 2.14
import PyTest 1.0
Item {
    height: 300
    width: 300
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
import QtQuick.Controls 2.14
import PyTest 1.0
Item {
    height: 300
    width: 300
    ${content}
}
"""
)


@pytest.fixture
def file1cas1test1(testdir):
    def wrapped(fn, *args, run=True):
        result = None
        testdir.makefile(
            ".qml",
            tst_BBB=BASE1CAS1TEST.substitute(fn=fn),
        )
        if run:
            result = testdir.runpytest("-s", *args)
        return testdir, result

    return wrapped


@pytest.fixture
def gabarit(testdir):
    def wrapped(content, *args, run=True):
        result = None
        testdir.makefile(
            ".qml",
            tst_BBB=GABARIT.substitute(content=content),
        )
        if run:
            result = testdir.runpytest("-s", *args)
        return testdir, result

    return wrapped
