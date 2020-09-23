from dataclasses import dataclass
from pathlib import Path
from string import Template
import re

import pytest
import requests

pytest_plugins = "pytester"


root = Path(__file__).parent


base = Template(
    """
import QtQuick 2.0
import PyTest 1.0
Item {
    ${content}
}
"""
)


@dataclass
class LineError:
    """first line and last line INCLUSIVELY"""

    start: int
    end: int
    msg: str


FILES = {
    "tst_compare.qml": [
        LineError(start=1194, end=1194, msg="who is wrong loadsh or qt ?")
    ],
    # "tst_compare_quickobjects.qml",
    # "tst_createTemporaryObject.qml",
    # "tst_datadriven.qml",
    # "tst_destroy.qml",
    # "tst_findChild.qml",
    # "tst_grabImage.qml",
    # "tst_selftests.qml",
    # "tst_stringify.qml",
    # "tst_tryVerify.qml",
}

base_url = Template(
    "https://code.qt.io/cgit/qt/qtdeclarative.git/plain/tests/auto/qmltest/selftests/${file}?h=5.15.1"
)


def findstart(content: str):
    for n, line in enumerate(content.split("\n")):
        if "TestCase" in line:
            return n - 1


def comment_know_errors(filename: str, content: str):
    lines = content.split("\n")

    for err in FILES[filename]:
        for n in range(err.start, err.end + 1):
            lines[n - 1] = "//" + lines[n - 1]  # file start 1 not 0
    return "\n".join(lines)


def format_for_test(content: str):
    # change internal comparaison name
    _compared = content.replace("qtest_compareInternal", "_compare")
    # strip start of the file
    start = findstart(_compared)
    stripped = "\n".join(_compared.split("\n")[start:])
    # add some lines to keep line number as original
    destripped = "//\n" * (start - 1) + stripped
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
    ],
)
@pytest.mark.xfail(reason="succeeds alone, but not in the whole test suite without")
def test_QtTest(testdir, filename, passed, failed, xpassed, xfailed):
    content = format_test_file("tst_compare.qml")
    # print(content)
    testdir.makefile(".qml", tst_compare=base.substitute(content=content))
    r = testdir.runpytest("-s")
    r.assert_outcomes(passed=passed, failed=failed, xpassed=xpassed, xfailed=xfailed)
