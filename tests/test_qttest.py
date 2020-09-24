import sys
from pathlib import Path
from string import Template
import re

import pytest
import requests
import attr

# pytest_plugins = "pytester"


root = Path(__file__).parent


base = Template(
    """
import QtQuick 2.0
import PyTest 1.0
import QtQuick.Window 2.2
Item {
    ${content}
}
"""
)


@attr.s(auto_attribs=True)
class LineError:
    """first line and last line INCLUSIVELY"""

    start: int
    end: int
    msg: str


FILES = {
    "tst_compare.qml": [
        # LineError(start=1194, end=1194, msg="who is wrong loadsh or qt ?")
    ],
    "tst_compare_quickobjects.qml": [],
    "tst_createTemporaryObject.qml": [],
    "tst_datadriven.qml": [],
    "tst_destroy.qml": [],
    "tst_findChild.qml": [],
    "tst_grabImage.qml": [],
    "tst_selftests.qml": [],
    "tst_stringify.qml": [],
    "tst_tryVerify.qml": [],
}

base_url = Template(
    "https://code.qt.io/cgit/qt/qtdeclarative.git/plain/tests/auto/qmltest/selftests/${file}?h=5.15.1"
)

END = "\r\n" if sys.platform == "win32" else "\n"


def findstart(content: str):
    for n, line in enumerate(content.splitlines()):
        if "TestCase" in line:
            return n - 1


def comment_know_errors(filename: str, content: str):
    lines = content.splitlines(keepends=False)

    for err in FILES[filename]:
        for n in range(err.start, err.end + 1):
            lines[n - 1] = "//" + lines[n - 1]  # file start 1 not 0
    return END.join(lines)


def format_for_test(content: str):
    # change internal comparaison name
    _compared = content  # content.replace("qtest_compareInternal", "_compare")
    # strip start of the file
    start = findstart(_compared)
    stripped = END.join(_compared.splitlines(keepends=False)[start:])
    # add some lines to keep line number as original
    destripped = "//END" * (start - 1) + stripped
    # rename TestCase
    name = re.search(r"name: \"(.+)\"", content).groups()[0]
    named = destripped.replace(name, "Test" + name)
    return named


def format_test_file(filename: str):
    path = root / "qt_tests" / filename
    # download if not already
    if not path.is_file():
        res = requests.get(base_url.substitute(file=filename))
        path.write_text(res.text)
    filecontent = path.read_text()
    commented = comment_know_errors(filename, filecontent)
    content = format_for_test(commented)
    return content


@pytest.mark.parametrize(
    "filename, passed, failed, xpassed, xfailed",
    [
        ("tst_compare.qml", 8, 0, 0, 2),
        ("tst_compare_quickobjects.qml", 0, 0, 0, 1),
        ("tst_tryVerify.qml", 1, 0, 0, 0),
        ("tst_findChild.qml", 1, 0, 0, 0),
        # ("tst_selftests.qml", 1, 0, 0, 0),
    ],
)
@pytest.mark.runalone()
def test_qtTest(testdir, filename, passed, failed, xpassed, xfailed):
    content = format_test_file(filename)
    # print(content)
    testdir.makefile(".qml", **{filename: base.substitute(content=content)})
    args = ["-vv"] if sys.platform == "win32" else ["-vv", "-s", "--no-qt-log"]
    r = testdir.runpytest(*args)
    r.assert_outcomes(passed=passed, failed=failed, xpassed=xpassed, xfailed=xfailed)
