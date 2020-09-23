from pathlib import Path
from string import Template

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


def test_compare(testdir):
    file = (root / "tst_compare.qml").read_text()
    content = file.replace("qtest_compareInternal", "_compare")

    def findstart(content):
        for n, line in enumerate(content.split("\n")):
            if "TestCase" in line:
                return n - 1

    start = findstart(content)
    content2 = "\n".join(content.split("\n")[start:])
    content3 = content2.replace("SelfTests_compare", "TestSelfTests_compare")
    # print(content3)

    testdir.makefile(".qml", tst_compare=base.substitute(content=content3))
    testdir.runpytest("-s")
