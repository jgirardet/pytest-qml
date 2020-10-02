from string import Template
import pytest


WINDOW_SHOWN = Template(
    """
import QtQuick 2.14
import PyTest 1.0
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


def test_compare_various_type(
    testdir,
):
    testdir.makefile(
        ".qml",
        tst_BBB="""
import QtQuick 2.0
import PyTest 1.0
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
        property date date3: new Date(2018, 8, 21)
        property color color1: "red"
        property color color2: "blue"
        property color color3: "blue"
        property url url1: "www.he.fr"
        property url url2: "www.ha.fr"
        property url url3: "www.ha.fr"
        property point point1: Qt.point(1,2)
        property point point2: Qt.point(1,3)
        property point point3: Qt.point(1,3)
        property rect rect1: Qt.rect(1,1, 10, 20)
        property rect rect2: Qt.rect(1,1, 10, 10)
        property rect rect3: Qt.rect(1,1, 10, 10)
        property size size1: Qt.size(10, 20)
        property size size2: Qt.size(10, 10)
        property size size3: Qt.size(10, 10)
        
        
        function test_compare() {
        compare(qtest_compareInternal(date1, date1), true)
        compare(qtest_compareInternal(date1, date2), false)
        compare(qtest_compareInternal(date2, date3), true)
        compare(qtest_compareInternal(color1, color1), true)
        compare(qtest_compareInternal(color1, color2), false)
        compare(qtest_compareInternal(color2, color3), true)
        compare(qtest_compareInternal(color1, color1), true)
        compare(qtest_compareInternal(rect1, rect2), false)
        compare(qtest_compareInternal(rect2, rect3), true)
        compare(qtest_compareInternal(rect1, rect1), true)
        compare(qtest_compareInternal(size1, size2), false)
        compare(qtest_compareInternal(size2, size3), true)
        compare(qtest_compareInternal(size1, size1), true)
        compare(qtest_compareInternal(url1, url2), false) // QTBUG-61297
        compare(qtest_compareInternal(url2, url3), true)
        compare(qtest_compareInternal(url1, url1), true)
        }
    }
    }
    """,
    )
    result = testdir.runpytest("-s", "-vv", "--no-qt-log")
    result.assert_outcomes(passed=1)


# def test_compare_without_raise(file1cas1test1):
#
#     t, r = file1cas1test1(
#         """
#     //verify(compare([],[],"",false))
#     //compare(_compare([null],[undefined]), false)
#      var r = /foo/;
#      var rm1 = /foo/m;
#     compare(_compare(r, rm1), false,)
#     """
#     )
#     # r.stdout.fnmatch_lines_random([f"*1 passed*"])
#     r.assert_outcomes(passed=1)


class TestTryCompare:
    def test_try_compare_timed_out(self, file1cas1test1):
        t, r = file1cas1test1("""tryCompare(testcase, "name", "Pas Bon", 100)""")
        r.stdout.fnmatch_lines_random(["*1 failed*", '*"TestBla" != "Pas Bon"*'])

    def test_try_compare_timed_bad_prop(self, file1cas1test1):
        t, r = file1cas1test1("""tryCompare(testcase, {}, "Pas Bon", 100)""")
        r.stdout.fnmatch_lines_random(
            [
                "*1 failed*",
                "*A property name as string or index is required for tryCompare*",
            ]
        )

    def test_try_compare_one_arg_missing(self, file1cas1test1):
        t, r = file1cas1test1("""tryCompare(testcase, "name")""")
        r.stdout.fnmatch_lines_random(
            ["*1 failed*", "*A value is required for tryCompare*"]
        )

    def test_try_compare_timeout_not_int(self, file1cas1test1):
        t, r = file1cas1test1(
            """tryCompare(testcase, "name", "Pas Bon", "notinttimerout")"""
        )
        r.stdout.fnmatch_lines_random(["*1 failed*", "*timeout should be a number*"])

    def test_try_compare_works_already_set(self, file1cas1test1):
        t, r = file1cas1test1(
            """
        windowShown=true
        tryCompare(testcase, "name", "TestBla",10)
        """
        )
        r.assert_outcomes(passed=1)

    def test_try_compare_works_after_timer(self, gabarit):
        t, r = gabarit(
            """
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
        """
        )
        r.assert_outcomes(passed=1)


class TestTryVerify:
    def test_try_verify_timed_out(self, file1cas1test1):
        t, r = file1cas1test1("""tryVerify(function(){return false}, 1)""")
        r.assert_outcomes(failed=1)
        r.stdout.fnmatch_lines_random(["*tryVerify fonction never got true*"])

    def test_try_verify_no_function(self, file1cas1test1):
        t, r = file1cas1test1("""tryVerify("bla")""")
        r.stdout.fnmatch_lines_random(
            [
                "*First argument must be a function*",
            ]
        )
        r.assert_outcomes(failed=1)

    def test_try_verify_timeout_not_int(self, file1cas1test1):
        t, r = file1cas1test1("""tryVerify(function(){return true}, "notAnInt")""")
        r.stdout.fnmatch_lines_random(
            ["*1 failed*", "*timeout argument must be a number*"]
        )
        r.assert_outcomes(failed=1)

    def test_try_compare_works(self, file1cas1test1):
        t, r = file1cas1test1(
            """
        tryVerify(function(){return true})
        """
        )
        r.assert_outcomes(passed=1)

    def test_try_compare_works_after_timer(self, gabarit):
        t, r = gabarit(
            """
        TestCase{
            id: testcase
            name: "TestTryVerify"
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
            function test_tryverify_timer() {
                timer.start()
                tryVerify(function(){return testcase.rien=="bbbb"}, 400)
            }
        }
        """
        )
        r.assert_outcomes(passed=1)


def test_try_window_shown_at_start_is_true_after_waining(file1cas1test1):
    t, r = file1cas1test1(
        """
    windowShown=true
    tryCompare(testcase, "windowShown", true,10)

    """
    )
    r.assert_outcomes(passed=1)


def test_try_window_shown_at_start_is_true_without_waiting(file1cas1test1):
    """don't know if it's a good thing...."""
    t, r = file1cas1test1(
        """
    windowShown=true
    compare(testcase.windowShown, true)
    """
    )
    r.assert_outcomes(passed=1)


def test_when_fail(gabarit):
    t, r = gabarit(
        """
    TestCase {
        name: "TestWhen"
        function test_when_fail() {
        }
        when: false
        Component.onCompleted: qmlbot.setSettings("whenTimeout", 100)
    }"""
    )
    r.assert_outcomes(failed=1)
    r.stdout.fnmatch_lines_random(["*property 'when' never got value 'true'*"])


#


def test_when_wait_and_pass(gabarit):
    t, r = gabarit(
        """
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
    """
    )
    r.assert_outcomes(passed=1)


def test_verify_pass(file1cas1test1):
    t, r = file1cas1test1(
        """
    verify(true)
    """
    )
    r.assert_outcomes(passed=1)


def test_verify_fail(file1cas1test1):
    t, r = file1cas1test1(
        """
    verify(false)
    """
    )
    r.assert_outcomes(failed=1)


def test_skip(file1cas1test1):
    t, r = file1cas1test1(
        """
    skip("easier than fix !!!")
    """
    )
    r.assert_outcomes(skipped=1)


def test_init(gabarit):
    t, r = gabarit(
        """
    TestCase {
        name: "TestBla"
        property string hello: "hello"
        function init () {hello = "bye"}
        function test_init(){
            compare(hello, "bye")
        }
    }
    """,
        "-vv",
    )
    r.assert_outcomes(passed=1)


def test_cleanup(gabarit):
    t, r = gabarit(
        """
    TestCase {
        name: "TestBla"
        property string hello: "hello"
        function cleanup () {throw new Error("just to see if cleanup called")}
        function test_init(){
        }
    }
    """
    )
    r.assert_outcomes(failed=1)
    r.stdout.fnmatch_lines_random(["*just to see if cleanup called*"])


def test_createTemporaryObjects(file1cas1test1):
    t, r = file1cas1test1(
        """
    var comp = Qt.createComponent("Rec.qml")
    var obj = createTemporaryObject(comp, parent, {"height":3});
    compare(obj.height, 3)
    compare(obj.width, 99)
    """,
        run=False,
    )
    t.makefile(".qml", Rec="""import QtQuick 2.0; Item {height: 66; width:99}""")
    r = t.runpytest("-s")
    r.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "action, mx, my, button, modifier, res",
    [
        ("mousePress", "0", "0", "Qt.LeftButton", "Qt.NoModifier", '"left"'),
        ("mousePress", "0", "0", "Qt.LeftButton", "Qt.NoModifier", '"left"'),
        ("mousePress", "2", "2", "Qt.LeftButton", "Qt.NoModifier", '""'),
        ("mousePress", "0", "0", "Qt.RightButton", "Qt.NoModifier", '"right"'),
        (
            "mousePress",
            "0",
            "0",
            "Qt.RightButton",
            "Qt.NoModifier",
            '"right"',
        ),  # double to check release button
        ("mousePress", "0", "0", "Qt.LeftButton", "Qt.ControlModifier", '"ctrlleft"'),
        ("mouseClick", "0", "0", "Qt.LeftButton", "Qt.NoModifier", '"leftR"'),
        (
            "mouseDoubleClickSequence",
            "0",
            "0",
            "Qt.LeftButton",
            "Qt.NoModifier",
            '"leftRleftR"',
        ),
        # ("mousePress", "2", "2", "Qt.LeftButton", '""'),
    ],
)
def test_mouse(gabarit, action, mx, my, button, modifier, res):
    content = Template(
        """
    TestCase {
        name: "TestMouse"
        when: windowShown
        function test_mouse(){
            button.text = ""
            ${action}(mousearea, ${mx},${my}, ${button},${modifier})
            compare(button.text,${res})
        }
    }
    Button {id:button; x:0 ;y:0 ;height:5; width:5; text:""}
    MouseArea {
        x: 10; y: 10; height: 1; width: 1
        id: mousearea
        acceptedButtons: Qt.AllButtons
        onPressed: {
            if (mouse.button == Qt.LeftButton) {
                if (mouse.modifiers & Qt.ControlModifier) {

                button.text=button.text +"ctrl"
                }
                button.text=button.text +"left"
            } else if (mouse.button == Qt.RightButton) {
                button.text = button.text + "right"
            } else {
                button.text = button.text + "other"
                }
        }
        onReleased: {
            button.text = button.text + "R"
        }
    }
    """
    )
    t, r = gabarit(
        content.substitute(
            action=action, mx=mx, my=my, button=button, modifier=modifier, res=res
        ),
        "-vv",
    )
    r.assert_outcomes(passed=1)


def test_mouse_release(gabarit):
    t, r = gabarit(
        """
    Button {
        id: button
    }
    TestCase {
        name: "TestBla"
        function test_release() {
            mousePress(button)
            compare(button.pressed, true)
            mouseRelease(button)
            compare(button.pressed, false)
        }
    }
    """
    )
    r.assert_outcomes(passed=1)


def test_mouse_move(gabarit):
    t, r = gabarit(
        """
    MouseArea {
        id: area
        hoverEnabled: true
        height: 100
        width: 100
    }
    TestCase {
        name: "TestBla"
        function test_move() {
            mouseMove(area, 62, 70)
            compare(area.mouseX, 62)
            compare(area.mouseY, 70)
        }
    }
    """
    )
    r.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "action, button, modifier, res",
    [
        ("keyClick", "Qt.Key_A", "Qt.NoModifier", "ar"),
        ("keyClick", "Qt.Key_A", "Qt.ControlModifier", "AR"),
        ("keyPress", "Qt.Key_A", "Qt.NoModifier", "a"),
        ("keyPress", "Qt.Key_A", "Qt.ControlModifier", "A"),
        ("keyRelease", "Qt.Key_A", "Qt.ControlModifier", "R"),
        ("keyRelease", "Qt.Key_A", "Qt.NoModifier", "r"),
        ("keySequence", '"a,a"', "Qt.NoModifier", "arar"),
    ],
)
def test_keyboard(gabarit, action, button, modifier, res):
    content = Template(
        """
    TestCase {
        name: "TestKeyboard"
        when: windowShown
        function test_keyboard(){
            textarea.forceActiveFocus() // neededon CI
            ${action}(${button},${modifier})
            compare(textarea.text,"${res}")
        }
        function test_keyboard2(){ 
            // we can press an already pressed key != not the case for mouse button
            textarea.forceActiveFocus() // needed on CI
            ${action}(${button},${modifier})
            compare(textarea.text,"${res}${res}")
        }
    }
    Text {
        id: textarea
        text: ""
        focus:true
        Keys.onPressed: {
           if (event.key == Qt.Key_A) {
                if (event.modifiers ==  Qt.ControlModifier) {
                    text=text + "A"} 
                else {text = text + "a"}
            }
        }
        Keys.onReleased: {
            if (event.key == Qt.Key_A) {
                if (event.modifiers ==  Qt.ControlModifier) {
                    text=text + "R"} 
                else {text = text + "r"}
            }
        }
    }
    """
    )
    t, r = gabarit(
        content.substitute(action=action, button=button, modifier=modifier, res=res),
        "-s",
        "-vv",
    )
    r.assert_outcomes(passed=2)


def test_expect_fail_fail(file1cas1test1):
    t, r = file1cas1test1(
        """
        expectFail("", "doit afficher passed malgree erreur")
        compare( 1,0)
    """
    )
    r.assert_outcomes(xfailed=1)


def test_expect_fail_pass(file1cas1test1):
    t, r = file1cas1test1(
        """
        expectFail("", "doit afficher passed malgree erreur")
        compare( 1,1)
    """,
    )
    r.assert_outcomes(xpassed=1)


def test_fail(file1cas1test1):
    t, r = file1cas1test1("""fail("test failed by user")""", "-vv", "-s")
    r.assert_outcomes(failed=1)


def test_inittTestcase(gabarit):
    t, r = gabarit(
        """
    TestCase {
        name: "aaa"
        function initTestCase(){
            name = "bbb"
        }
        function test_aaa_devenu_bbb() {
            compare(name, "bbb")
        }
    }
    """
    )
    r.assert_outcomes(passed=1)


def test_cleanupTestcase_and_completed(gabarit):
    t, r = gabarit(
        """
    Rectangle {
        id: rien
        x: 5
    }
    TestCase {
        id: firsttestcase
        name: "aaaFirst"
        function test_some(){
            compare(rien.x,5)
            compare(completed,false)
            rien.x = 9
            
            
        }
        function cleanupTestCase(){
            print("cleannenfenze")
            rien.x = 15
        }
    }
    TestCase {
        name: "bbbSecond"
        function test_after_cleaup_of_other(){
            compare(rien.x, 15)
            compare(firsttestcase.completed, true)
            
        }
    }
    """
    )
    r.assert_outcomes(passed=2)


def test_fuzzycompare_success_float(file1cas1test1):
    t, r = file1cas1test1("""fuzzyCompare(0.4,0.5, 0.1)""", "-vv", "-s")
    r.assert_outcomes(passed=1)


def test_fuzzycompare_fail_float(file1cas1test1):
    t, r = file1cas1test1("""fuzzyCompare(0.4,0.5, 0.01)""", "-vv", "-s")
    r.assert_outcomes(failed=1)


def test_fuzzycompare_success_color(file1cas1test1):
    t, r = file1cas1test1("""fuzzyCompare("red","#ff0000", 0)""", "-vv", "-s")
    r.assert_outcomes(passed=1)


def test_fuzzycompare_fail_float(file1cas1test1):
    t, r = file1cas1test1("""fuzzyCompare("red","#f00000", 0)""", "-vv", "-s")
    r.assert_outcomes(failed=1)


def test_fuzzycompare_fail_no_good_value(file1cas1test1):
    t, r = file1cas1test1("""fuzzyCompare(["aa"],"#f00000", 0)""", "-vv", "-s")
    r.assert_outcomes(failed=1)


def test_signa_spy_wait(gabarit):
    t, r = gabarit(
        """
    Item {
        id: item
        signal noarg()
        signal withargs(string arg1, int arg2)
    }
    SignalSpy {
        id: spy1
        target: item
        signalName: "noarg"
    }
    SignalSpy {
        id: spy2
        target: item
        signalName: "withargs"
    }
    TestCase {
        function init() {
            spy1.clear()
            spy2.clear()
        }

        function test_no_arg() {
            item.noarg()
            spy1.wait(0)
            compare(spy1.count, 1)
            item.noarg()
            compare(spy1.count, 2)
            spy1.clear() // test also clear
            compare(spy1.count, 0)
            compare(spy1.signalArguments,[])
        }
        function test_with_args() {
            item.withargs("aaa",3)
            spy2.wait(0)
            compare(spy2.count, 1)
            item.withargs("bbb",1)
            spy2.wait(0)
            compare(spy2.count, 2)
            qmlbot.debug(JSON.stringify(spy2.signalArguments))
            compare(spy2.signalArguments,[{"0":"aaa","1":3},{"0":"bbb","1":1}]
)
            spy2.clear() // test also clear
            compare(spy2.count, 0)
            compare(spy2.signalArguments,[])
        }
        function test_error() {
            spy1.wait(0)
        }
    }
    """
    )
    r.assert_outcomes(passed=2, failed=1)
    r.stdout.fnmatch_lines_random(
        ["*signal noarg emitted 0 times but 1  was expected*"]
    )


def test_data_driven(gabarit):
    t, r = gabarit(
        """
    TestCase {
        function test_bla_data() {return [{"tag":"un", "val":1}, {"tag":"deux", "val":2},{"val":3}]}
        function test_bla(data) {
            compare(data.val, 1)
            
        }
    }
    """
    )
    r.assert_outcomes(passed=1, failed=2)
    r.stdout.fnmatch_lines_random(
        ["*test_bla_deux FAILED*", "*test_bla_un PASSED*", "*test_bla_2 FAILED*"]
    )


def test_data_driven_init_data(gabarit):
    t, r = gabarit(
        """
    TestCase {
        function init_data() {return [{"tag":"un", "val":1}, {"tag":"deux", "val":2},{"val":3}]}
        function test_bla(data) {
            compare(data.val, 1)
            
        }
    }
    """
    )
    r.assert_outcomes(passed=1, failed=2)
    r.stdout.fnmatch_lines_random(
        [
            "*test_bla_deux FAILED*",
            "*test_bla_un PASSED*",
            "*test_bla_2 FAILED*",
        ]
    )


def test_data_driven_arg_forgot(gabarit):
    t, r = gabarit(
        """
    TestCase {
        function init_data() {return [{"val":1}]}
        function test_thought(data) {
        }
        function test_forgot() {
        }
    }
    """
    )
    r.assert_outcomes(passed=2)
    r.stdout.fnmatch_lines_random(
        [
            "*no data supplied for test_forgot_0",
        ]
    )
