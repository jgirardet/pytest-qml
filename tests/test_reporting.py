from pathlib import Path

import pytest
from pytestqml.reporting import get_error_line_in_stack, pick_error_context

example_25 = """constructor@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/utils.mjs:21
constructor@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/utils.mjs:46
compare@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/TestCase.qml:121
test_compare@file:///tmp/pytest-of-jimmy/pytest-159/test_compare_various_type1/tst_BBB.qml:25
runOneTest@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/TestCase.qml:88
onTestToRunChanged@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/TestCase.qml:68"""

example_11 = """constructor@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/utils.mjs:21
tryVerify@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/TestCase.qml:260
test_fonction@file:///tmp/pytest-of-jimmy/pytest-159/test_try_verify_timeout_not_int0/tst_BBB.qml:11
runOneTest@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/TestCase.qml:88
onTestToRunChanged@file:///home/jimmy/dev/pytest-qml/src/pytestqml/PyTest/TestCase.qml:68"""


@pytest.mark.parametrize(
    "module, stack, lineno",
    [
        ("tst_BBB.qml", example_25, 25),
        ("tst_B.qml", example_25, None),
        ("tst_BBB.qml", example_11, 11),
        ("tst_B.qml", example_11, None),
    ],
)
def test_get_error_line_in_stack(module, stack, lineno):
    assert get_error_line_in_stack(module, stack) == lineno


@pytest.mark.parametrize(
    "module, test,line_no, err_type, msg,res",
    [
        (
            "assets/pick_error_context.qml",
            "test_simple",
            18,
            "GrosError",
            "oh lala",
            [
                "\x1b[34m17: \x1b[0m\x1b[33m        function test_simple(){\x1b[0m",
                "\x1b[34m18: \x1b[0m            compare(1,1)\x1b[31m GrosError ===>  oh lala\x1b[0m",
                "\x1b[34m19: \x1b[0m\x1b[33m        }\x1b[0m",
            ],
        ),
        (
            "assets/pick_error_context.qml",
            "test_custom_comp",
            27,
            "ClickError",
            "Ceci n'est pas une souris",
            [
                "\x1b[34m24: \x1b[0m\x1b[33m        function test_custom_comp(){\x1b[0m",
                '\x1b[34m25: \x1b[0m            let comp = Qt.createComponent("../Comp.qml")',
                "\x1b[34m26: \x1b[0m            let c = createTemporaryObject(comp, item)",
                "\x1b[34m27: \x1b[0m            mouseClick(c)\x1b[31m ClickError ===>  Ceci n'est pas une souris\x1b[0m",
                '\x1b[34m28: \x1b[0m            compare(c.text, "bla")',
                "\x1b[34m29: \x1b[0m\x1b[33m        }\x1b[0m",
            ],
        ),
    ],
)
def test_pick_error_context(
    module: str, test: str, line_no: int, err_type: str, msg: str, res: list
):
    module = (Path(__file__).parent / module).resolve()
    res1 = pick_error_context(module, test, line_no, err_type, msg)
    assert res1 == res
