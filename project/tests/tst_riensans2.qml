import QtQuick 2.14
import PyTest 1.0
import ".."
import MyNewType 1.0

Item {
    id: item
    Bla {
        id: bla
    }
    Text {
        id: textarea
        text: ""
        focus:true
        Keys.onPressed: {
           if (event.key == Qt.Key_A) {
                if (event.modifiers ==  Qt.ControlModifier) {
                    text="A"
                } else {
                    text = "a"
                }
        }
    }
    }
    TestCase {
        name: "TestRienSans2"
        function test_simple(){
            compare("Hello","Good bye")
        }

        function test_deuxieme(){
            compare(1,1)
        }
//        function test_custom_comp(){
//            let comp = Qt.createComponent("../Comp.qml")
//            let c = createTemporaryObject(comp, item)
//            mouseClick(c)
//            compare(c.text, "bla")
//        }
        function test_custom_type1(){
            compare(bla.rien, "rien")
        }
        function test_custom_type2(){
            compare(bla.rien, "rien")
        }
        function test_custom_type3(){
            compare(bla.rien, "rien")
        }
        function test_keyboard() {
            textarea.forceActiveFocus()
            textarea.text=""
            keyClick(Qt.Key_A, Qt.ControlModifier)
            compare(textarea.text,"A")
            keyClick(Qt.Key_A)
            compare(textarea.text,"a")
        }
//        function test_keyboardsequ() {
//            textarea.forceActiveFocus()
//            textarea.text=""
//            keySequence("abcd")
//            compare(textarea.text,"A")
//            keyClick(Qt.Key_A)
//            compare(textarea.text,"a")
//        }
        function test_xfail_fail() {
            expectFail("","reason of  xfailed")
//            print("should XFAIL")
//            console.error("ojlihk")
//            console.critical("ojlihk")
            compare(1,0)
        }
        function test_xfail_pass_() {
            expectFail("","should xpassed")
            compare(1,1)
        }

    }
}