# -*- coding: utf-8 -*-
import os
import re
import time
from pathlib import Path
from string import Template

import pytest
import pytestqml

TESTCASE = (Path(pytestqml.__path__[0]) / "PyTest" / "TestCase.qml").read_text()

ITEM_EMPTY = """
import QtQuick 2.14
Item {
}
"""

ITEM_1Case_EMPTY = """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {}
}
"""

ITEM_1Case_1Test = """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {
        name: "TestBla"
        function test_bla() {}
    }
}
"""

ITEM_1Case_2Test = """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {
        name: "TestBla"
        function test_bla() {}
        function test_blabla() {}
    }
}
"""

ITEM_2Case_4Test = """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {
        name: "TestBla"
        function test_bla() {}
        function test_blabla() {}
    }
    TestCase {
        name: "TestBli"
        function test_bli() {}
        function test_blibli() {}
    }
}
"""

ITEM_1Case_1Test_cp = """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {
        name: "TestBla"
        function test_bla() {
            let avar = cp.aCpVar
        }
    }
}
"""

ITEM_1Case_1Test_pass = """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {
        name: "TestBla"
        function test_bla() {}
    }
}
"""
ITEM_1Case_1Test_pass_async = Template(
    """
import QtQuick 2.14
import PyTest 1.0
Item {
    TestCase {
        name: "TestBla"
        function test_bla_async() {
            let sDate = Date.now()
            wait(${delay})
            let eDate = Date.now()
            qmlbot.debug("||||"+(eDate-sDate)+"||||")
        }
        
        
    }
}
"""
)


DIVERS = """
import QtQuick 2.14
import PyTest 1.0
import QtQuick.Controls 2.14
Button {
    id: button
    height: 200
    width:200
    text: "1"
    onClicked: {
        print("clicked")
        qmlbot.debug("clicked bot")
        text = text  + "+1"
        }
    TestCase {
        id: testcase
        name: "TestBla"
        when: false
        function test_bla_show() {
        }
        Component.onCompleted: {
        qmlbot.wait(3000)
        when = true
        }
    }
    BusyIndicator {
        y:20
    }
}
"""


def test_collect_1_file_0_Case_0_test(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_EMPTY)
    result = testdir.runpytest("--co")
    result.stdout.fnmatch_lines_random(["collected 0 items"])


def test_collect_1_file_1_Case_0_test(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_1Case_EMPTY)
    result = testdir.runpytest("--co")
    result.stdout.fnmatch_lines_random(["collected 0 items"])


def test_collect_1_file_1_Case_1_test(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_1Case_1Test)
    result = testdir.runpytest("--co")
    result.stdout.fnmatch_lines_random(
        ["collected 1 item", "<QMLFile tst_BBB.qml>", "  <QMLItem TestBla::test_bla>"]
    )


def test_collect_1_file_1_Case_2_test(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_1Case_2Test)
    result = testdir.runpytest("--co")
    result.stdout.fnmatch_lines_random(
        [
            "collected 2 items",
            "<QMLFile tst_BBB.qml>",
            "  <QMLItem TestBla::test_bla>",
            "  <QMLItem TestBla::test_blabla>",
        ]
    )


def test_collect_1_file_2_Case_4_test(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_2Case_4Test)
    result = testdir.runpytest("--co")
    result.stdout.fnmatch_lines_random(
        [
            "collected 4 items",
            "<QMLFile tst_BBB.qml>",
            "  <QMLItem TestBla::test_bla>",
            "  <QMLItem TestBla::test_blabla>",
            "  <QMLItem TestBli::test_bli>",
            "  <QMLItem TestBli::test_blibli>",
        ]
    )


def test_collect_2_file_3_Case_6_test(testdir):
    testdir.makefile(".qml", tst_AAA=ITEM_1Case_2Test)
    testdir.makefile(".qml", tst_BBB=ITEM_2Case_4Test)
    result = testdir.runpytest("--co")
    result.stdout.fnmatch_lines_random(
        [
            "collected 6 items",
            "<QMLFile tst_AAA.qml>",
            "  <QMLItem TestBla::test_bla>",
            "  <QMLItem TestBla::test_blabla>",
            "<QMLFile tst_BBB.qml>",
            "  <QMLItem TestBla::test_bla>",
            "  <QMLItem TestBla::test_blabla>",
            "  <QMLItem TestBli::test_bli>",
            "  <QMLItem TestBli::test_blibli>",
        ]
    )


def test_collect_1_file_1_Case_1_test_pass(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_1Case_1Test_pass)
    result = testdir.runpytest("-s")
    result.assert_outcomes(passed=1)


def test_collect_1_file_1_Case_1_test_pass_async(testdir):
    # testdir.makefile(".qml", tst_AAA=ITEM_1Case_1Test_pass)
    testdir.makefile(".qml", tst_AAA=ITEM_1Case_1Test_pass_async.substitute(delay=0))
    # print(Path(str(testdir), "tst_AAA.qml").read_text())
    result = testdir.runpytest("-s")
    result.stdout.fnmatch_lines_random(["*1 passed*"])
    find_time = re.compile(r".*\|\|\|\|(\d+)\|\|\|\|.*")
    time1 = int(find_time.search(result.stdout.str()).groups()[0])

    testdir.makefile(".qml", tst_AAA=ITEM_1Case_1Test_pass_async.substitute(delay=100))
    result = testdir.runpytest("-s", "-vv")
    time2 = int(find_time.search(result.stdout.str()).groups()[0])
    result.stdout.fnmatch_lines_random(["*1 passed*"])

    assert time2 - time1 == pytest.approx(100, 10)  # 10% of error



def test_collect_with_context_propertie(testdir):
    testdir.makefile(".qml", tst_BBB=ITEM_1Case_1Test_cp)
    testdir.makeconftest('''
    from pytestqml.qt import QObject, Property
    class Cp(QObject):
        @Property(str)
        def aVar(self):
            return "this is aVar"
    def pytest_qml_context_properties():
        return {"cp":Cp()}
        ''')
    result = testdir.runpytest("-s")
    result.assert_outcomes(passed=1)

@pytest.mark.xfail(reason="succeeds alone, but not in the whole test suite without")
def test_register_new_qml_type(testdir):
    testdir.makefile(".qml", tst_AAA="""
    import QtQuick  2.0
    import PyTest 1.0
    import MyType 1.0
    Item {
        MyObj {id:obj}
        TestCase {
            name: "TestType"
            function test_add_type() 
            {
            compare(obj.aaa,"aaa" )
            }
        }
    }
    """)
    testdir.makeconftest('''
    from pytestqml.qt import qmlRegisterType, QObject, Property
    class MyObj(QObject):
        @Property(str)
        def aaa(self):
            return "aaa"
    def pytest_configure():
        qmlRegisterType(MyObj, "MyType", 1, 0, "MyObj")
    ''')
    result = testdir.runpytest("-s")
    result.assert_outcomes(passed=1)


#
# def test_collect_2_qml_files(testdir):
#     testdir.makefile(".qml", tst_AAA=ITEM_EMPTY)
#     testdir.makefile(".qml", tst_BBB=ITEM_EMPTY)
#     result = testdir.runpytest("-s")
#     result.stdout.fnmatch_lines_random([
#         "collected 2 items"
#     ])
#
#
# def test_collect_only_tst_dot_qml_file(testdir):
#     testdir.makefile(".qml", tst_AAA=ITEM_EMPTY)
#     testdir.makefile(".py", tst_BBB="")
#     testdir.makefile(".qm", tst_CCC=ITEM_EMPTY)
#     result = testdir.runpytest("-s")
#     result.stdout.fnmatch_lines_random([
#         "collected 1 item"
#     ])
#
#
#
#
# def test_collect_fail_if_view_setSource_fail(testdir):
#     testdir.makefile(".qml", tst_AAA="")
#     result = testdir.runpytest("")
#     result.stdout.fnmatch_lines_random([
#         "*tst_AAA.qml: File is empty*",
#         "*collected 0 items / 1 error*"
#     ])
#
#
#
# def test_collect_py_test_and_ts_qml(testdir):
#     testdir.makefile(".qml", tst_AAA=ITEM_EMPTY)
#     testdir.makefile(".qml", tst_BBB=ITEM_EMPTY)
#     testdir.makepyfile(test_bla="""
# def test_aaa():
#     assert True
# """)
#     result = testdir.runpytest("-s")
#     result.stdout.fnmatch_lines([
#         "*collected 3 items*",
#     ])
#
# #
#
#
# def test_collect_skip_qml(testdir):
#     testdir.makefile(".qml", tst_AAA=ITEM_EMPTY)
#     testdir.makefile(".qml", tst_BBB=ITEM_EMPTY)
#     testdir.makeconftest('''
# from pytestqml.plugin import collect_any_tst_files
# def  pytest_collect_file(path, parent):
#     return  collect_any_tst_files(path, parent)
#     ''')
#     testdir.makepyfile(test_bla="""
# def test_aaa():
#     assert True
# """)
#     result = testdir.runpytest("--skip-qml")
#     result.stdout.fnmatch_lines([
#         "*collected 1 item*",
#     ])
#
#
# def test_collect_qmlbot(testdir):
#     testdir.makefile(".qml", tst_AAA="""
# import QtQuick 2.14
# Item {
#     property string text: ctx.aaa
#     Component.onCompleted: {
#         print(qmlbot.debug(text))
#     }
# }
# """)
#     testdir.makeconftest('''
# from pytestqml.plugin import collect_any_tst_files
# from pytestqml.qt import QtCore, Property
# def  pytest_collect_file(path, parent):
#     class Ctx(QtCore.QObject):
#
#         @Property(str)
#         def aaa(self):
#             return "hello, folks !"
#     ctx = Ctx()
#     return  collect_any_tst_files(path, parent, context_properties={"ctx":ctx})
#     ''')
#     testdir.makepyfile(test_bla="""
# def test_aaa():
#     assert True
# """)
#     result = testdir.runpytest("-s")
#     result.stdout.fnmatch_lines([
#         "*hello, folks !*",
#     ])
#


#
# def test_bar_fixture(testdir):
#     """Make sure that pytest accepts our fixture."""
#
#     # create a temporary pytest test module
#     testdir.makepyfile("""
#         def test_sth(bar):
#             assert bar == "europython2015"
#     """)
#
#
#
#     # run pytest with the following cmd args
#     result = testdir.runpytest(
#         '--foo=europython2015',
#         '-v'
#     )
#
#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_sth PASSED*',
#     ])
#
#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0
#
#
# def test_help_message(testdir):
#     result = testdir.runpytest(
#         '--help',
#     )
#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         'qml:',
#         '*--foo=DEST_FOO*Set the value for the fixture "bar".',
#     ])

#
# def test_hello_ini_setting(testdir):
#     testdir.makeini("""
#         [pytest]
#         HELLO = world
#     """)
#
#     testdir.makepyfile("""
#         import pytest
#
#         @pytest.fixture
#         def hello(request):
#             return request.config.getini('HELLO')
#
#         def test_hello_world(hello):
#             assert hello == 'world'
#     """)
#
#     result = testdir.runpytest('-v')
#
#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_hello_world PASSED*',
#     ])
#
#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0
