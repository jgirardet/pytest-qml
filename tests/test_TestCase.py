from string import Template
import pytest

COMPARE = Template(
    """
import QtQuick 2.14
import PythonTestCase 1.0
Item {
    Item {
        id: obj1
    }
    Item {
        id: obj2
    }
    TestCase {
        name: "TestBla"
        property date date1: new Date(2018, 8, 22) 
        property date date2: new Date(2018, 8, 21)
        property color color1: "red"
        property color color2: "blue"
        property url url1: "www.he.fr"
        property url url2: "www.ha.fr"
        property point point1: Qt.point(1,2)
        property point point2: Qt.point(1,3)
        property rect rect1: Qt.rect(1,1, 10, 20)
        property rect rect2: Qt.rect(1,1, 10, 10)
        property size size1: Qt.size(10, 20)
        property size size2: Qt.size(10, 10)
        function test_compare() {
            compare(${lhs},${rhs})
        }
        
    }
}
"""
)
WINDOW_SHOWN = Template(
    """
import QtQuick 2.14
import PythonTestCase 1.0
Item {
    id: root
    TestCase {
        name: "ClickTest"
        when: windowShown
        function test_click() {
            button.clicked();
            compare(button.text, "Clicked");
        }
    }
}"""
)


@pytest.mark.parametrize(
    "lhs, rhs, res",
    [
        ('"a"', '"a"', "passed"),
        ('"a"', '"b"', "failed"),
        ("1", "1", "passed"),
        ("1", '"1"', "failed"),
        ("[1,2,3]", "[1,2,3]", "passed"),
        ("[1,2,3]", "[1,1,3]", "failed"),
        ('{"aa":"bb", "cc":"cc"}', '{"aa":"bb", "cc":"cc"}', "passed"),
        ('{"aa":"bb", "cc":"cc"}', '{"aa":"bb", "cc":"XX"}', "failed"),
        ("obj1", "obj1", "passed"),
        ("obj1", "obj2", "failed"),
        ("date1", "date1", "passed"),
        ("date1", "date2", "failed"),
        ("color1", "color1", "passed"),
        ("color1", "color2", "failed"),
        ("url1", "url1", "passed"),
        ("url1", "url2", "failed"),
        ("point1", "point1", "passed"),
        ("point1", "point2", "failed"),
        ("rect1", "rect1", "passed"),
        ("rect1", "rect2", "failed"),
        ("size1", "size1", "passed"),
        ("size1", "size2", "failed"),
    ],
)
def test_compare_various_type(testdir, lhs, rhs, res):
    testdir.makefile(".qml", tst_BBB=COMPARE.substitute(lhs=lhs, rhs=rhs))
    result = testdir.runpytest("-s")
    result.stdout.fnmatch_lines_random([f"*1 {res}*"])
    if res == "failed":
        result.stdout.fnmatch_lines_random([f"*CompareError*"])


def test_try_compare_timed_out(file1cas1test1):
    t, r = file1cas1test1("""tryCompare(testcase, "name", "Pas Bon", 100)""")
    r.stdout.fnmatch_lines_random(["*1 failed*", '*"TestBla" != "Pas Bon"*'])


def test_try_compare_timed_bad_prop(file1cas1test1):
    t, r = file1cas1test1("""tryCompare(testcase, {}, "Pas Bon", 100)""")
    r.stdout.fnmatch_lines_random(["*1 failed*", "*A property name as string or index is required for tryCompare*"])


def test_try_compare_one_arg_missing(file1cas1test1):
    t, r = file1cas1test1("""tryCompare(testcase, "name")""")
    r.stdout.fnmatch_lines_random(["*1 failed*", "*A value is required for tryCompare*"])


def test_try_compare_timeout_not_int(file1cas1test1):
    t, r = file1cas1test1("""tryCompare(testcase, "name", "Pas Bon", "notinttimerout")""")
    r.stdout.fnmatch_lines_random(["*1 failed*", "*timeout should be a number*"])

def test_try_compare_works_already_set(file1cas1test1):
    t, r = file1cas1test1("""
    windowShown=true
    tryCompare(testcase, "name", "TestBla",10)
    """)
    r.assert_outcomes(passed=1)




def test_try_compare_works_after_timer(gabarit):
    t, r = gabarit("""
    TestCase{
        id: testcase
        name: "TestTryCompare"
        property string rien: "aaaaa"
        Timer {
            id: timer
             interval: 100
             repeat:false
             running: false
             onTriggered: {
             testcase.rien = "bbbb"
             
             }
          }
        function test_blafefzefez() {
            timer.start()
            tryCompare(testcase, "rien", "bbbb", 400)
        }
    }
    """)
    r.assert_outcomes(passed=1)


def test_try_window_shown_at_start_is_true_after_waining(file1cas1test1):
    t, r = file1cas1test1("""
    windowShown=true
    tryCompare(testcase, "windowShown", true,10)

    """)
    r.assert_outcomes(passed=1)


def test_try_window_shown_at_start_is_true_without_waiting(file1cas1test1):
    """don't know if it's a good thing...."""
    t, r = file1cas1test1("""
    windowShown=true
    compare(testcase.windowShown, true)
    """)
    r.assert_outcomes(passed=1)


def test_when_fail(gabarit):
    t, r = gabarit("""
    TestCase {
        name: "TestWhen"
        function test_when_fail() {
        }
        when: false
        Component.onCompleted: qmlbot.setSettings("whenTimeout", 100)
    }""")
    r.assert_outcomes(failed=1)
    r.stdout.fnmatch_lines_random(["*property 'when' never got value 'true'*"])

#

def test_when_wait_and_pass(gabarit):
    t, r = gabarit("""
    TestCase{
        id: testcase
        name: "TestTryCompare"
        property bool rien: false
        Timer {
            id: timer
             interval: 10
             repeat:false
             running: false
             onTriggered: {
             testcase.rien = true

             }
          }
        when: rien
        function test_blafefzefez() {
            
        }
        Component.onCompleted: timer.start()
    }
    """)
    r.assert_outcomes(passed=1)


def test_verify_pass(file1cas1test1):
    t, r = file1cas1test1("""
    verify(true)
    """)
    r.assert_outcomes(passed=1)


def test_verify_fail(file1cas1test1):
    t, r = file1cas1test1("""
    verify(false)
    """)
    r.assert_outcomes(failed=1)

def test_skip(file1cas1test1):
    t,r = file1cas1test1("""
    skip("easier than fix !!!")
    """)
    r.assert_outcomes(skipped=1)


def test_init(gabarit):
    t, r = gabarit("""
    TestCase {
        name: "TestBla"
        property string hello: "hello"
        function init () {hello = "bye"}
        function test_init(){
            compare(hello, "bye")
        }
    }
    """, "-vv")
    r.assert_outcomes(passed=1)