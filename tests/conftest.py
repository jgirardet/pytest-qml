import re
from string import Template

import pytest
from _pytest.nodes import Item

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
            result = testdir.runpytest("-s", "-vv", *args)
        return testdir, result

    return wrapped


def pytest_runtest_setup(item: Item):
    """skip runalone test when global run"""

    if item.get_closest_marker("runalone"):
        name = re.match(r"test_([^\[]+)", item.name).group()
        if not item.config.args or not any(
            re.match(fr".*\:\:{name}", arg) for arg in item.config.args
        ):
            pytest.skip(msg="should run alone")
