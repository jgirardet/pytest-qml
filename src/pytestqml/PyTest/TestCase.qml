import QtQuick 2.0
import "utils.mjs" as U
import QtQuick.Window 2.2

Item {
        id: root

        property bool isPythonTestCase: true

        /*
            All collected tests of this TestCase
            collected = {"testName":test_function}
        */
        property var collected: ({})

        /*
            Name of the TestCase
        */
        property string name: ""

        /*
            TestCase Running
        */
        property string running: ""

        /*
            Execute TestCase when condition is true
        */
        property bool when: true
        /*
            Name of the running test. Setting testToRun to "testname" triggers
            running the test "testname".
        */
        property string testToRun: ""

        /*
            Object containing result of the test execution
            with the error (type, message, stack, ...)
             Empty {} if test is successful
        */
        property var result

        /*
            Emit the end of execution. Does not means "success" (see result).
        */
        signal  testCompleted()

        /*
            The window isExposed.
        */
        property bool windowShown: qmlbot ? qmlbot.windowShown : false

        /*
            temporaryObjects: created by createTemporaryObject. cleaned up at end of the test
        */
        property var temporaryObjects: []

        onTestToRunChanged:{
            try {
            tryCompare(root, "when", true, qmlbot.settings("whenTimeout"))
            } catch(err) {
            result = err.toObj()
            running=false
            testCompleted()
            return result
         }
            runOneTest(testToRun)
        }


      function collectTests() {

        for (const [key, value] of Object.entries(root)){
          if (key.startsWith("test_")){
            collected[key] = value
            }

        }

        }

     function runOneTest(testName) {
        running=true
        let res= {}
        try {
          init()
          collected[testName]()
            }
        catch (err){
            if (err.type) {
                res = err.toObj()
            } else {
                 res = {"type": err.name, "message": err.message, "stack": err.stack}
            }
         }
        try {
            cleanup()
            temporaryObjects = []
        } catch (cleanupErr) {
            let error = new U.CleanupError(cleanupErr.message, {"other":res})
            error.stack  = cleanupErr.stack
            res = error.toObj()
            qmlbot.debug(res)
        }
        result = res
        running=false
        testCompleted()
        return res
    }

/*
Bellow this line you can find the QtTest PublicAPI
*/

    /*
        cleanup the current test
    */
    function cleanup() {
    }


    /*! \internal */
    // Determine what is o.
    // Discussions and reference: http://philrathe.com/articles/equiv
    // Test suites: http://philrathe.com/tests/equiv
    // Author: Philippe Rathé <prathe@gmail.com>
    function qtest_typeof(o) {
        if (typeof o === "undefined") {
            return "undefined";

        // consider: typeof null === object
        } else if (o === null) {
            return "null";

        } else if (o.constructor === String) {
            return "string";

        } else if (o.constructor === Boolean) {
            return "boolean";

        } else if (o.constructor === Number) {

            if (isNaN(o)) {
                return "nan";
            } else {
                return "number";
            }
        // consider: typeof [] === object
        } else if (o instanceof Array) {
            return "array";

        // consider: typeof new Date() === object
        } else if (o instanceof Date) {
            return "date";

        // consider: /./ instanceof Object;
        //           /./ instanceof RegExp;
        //          typeof /./ === "function"; // => false in IE and Opera,
        //                                          true in FF and Safari
        } else if (o instanceof RegExp) {
            return "regexp";

        } else if (typeof o === "object") {
            if ("mapFromItem" in o && "mapToItem" in o) {
                return "declarativeitem";  // @todo improve detection of declarative items
            } else if ("x" in o && "y" in o && "z" in o) {
                return "vector3d"; // Qt 3D vector
            }
            return "object";
        } else if (o instanceof Function) {
            return "function";
        } else {
            return undefined;
        }
    }

    /*! \internal */
    // Test for equality
    // Large parts contain sources from QUnit or http://philrathe.com
    // Discussions and reference: http://philrathe.com/articles/equiv
    // Test suites: http://philrathe.com/tests/equiv
    // Author: Philippe Rathé <prathe@gmail.com>
    function qtest_compareInternal(act, exp) {
        var success = false;
        if (act === exp) {
            success = true; // catch the most you can
        } else if (act === null || exp === null || typeof act === "undefined" || typeof exp === "undefined") {
            success = false; // don't lose time with error prone cases
        } else {
            var typeExp = qtest_typeof(exp), typeAct = qtest_typeof(act)
            if (typeExp !== typeAct) {
                // allow object vs string comparison (e.g. for colors)
                // else break on different types
                if ((typeExp === "string" && (typeAct === "object") || typeAct == "declarativeitem")
                 || ((typeExp === "object" || typeExp == "declarativeitem") && typeAct === "string")) {
                    success = (act == exp)
                }
            } else if (typeExp === "string" || typeExp === "boolean" ||
                       typeExp === "null" || typeExp === "undefined") {
                if (exp instanceof act.constructor || act instanceof exp.constructor) {
                    // to catch short annotaion VS 'new' annotation of act declaration
                    // e.g. var i = 1;
                    //      var j = new Number(1);
                    success = (act == exp)
                } else {
                    success = (act === exp)
                }
            } else if (typeExp === "nan") {
                success = isNaN(act);
            } else if (typeExp === "number") {
                // Use act fuzzy compare if the two values are floats
                if (Math.abs(act - exp) <= 0.00001) {
                    success = true
                }
            } else if (typeExp === "array") {
                success = qtest_compareInternalArrays(act, exp)
            } else if (typeExp === "object") {
                success = qtest_compareInternalObjects(act, exp)
            } else if (typeExp === "declarativeitem") {
                success = qtest_compareInternalObjects(act, exp) // @todo improve comparison of declarative items
            } else if (typeExp === "vector3d") {
                success = (Math.abs(act.x - exp.x) <= 0.00001 &&
                           Math.abs(act.y - exp.y) <= 0.00001 &&
                           Math.abs(act.z - exp.z) <= 0.00001)
            } else if (typeExp === "date") {
                success = (act.valueOf() === exp.valueOf())
            } else if (typeExp === "regexp") {
                success = (act.source === exp.source && // the regex itself
                           act.global === exp.global && // and its modifers (gmi) ...
                           act.ignoreCase === exp.ignoreCase &&
                           act.multiline === exp.multiline)
            }
        }
        return success
    }

    /*! \internal */
    function qtest_compareInternalObjects(act, exp) {
        var i;
        var eq = true; // unless we can proove it
        var aProperties = [], bProperties = []; // collection of strings

        // comparing constructors is more strict than using instanceof
        if (act.constructor !== exp.constructor) {
            return false;
        }

        for (i in act) { // be strict: don't ensures hasOwnProperty and go deep
            aProperties.push(i); // collect act's properties
            if (!qtest_compareInternal(act[i], exp[i])) {
                eq = false;
                break;
            }
        }

        for (i in exp) {
            bProperties.push(i); // collect exp's properties
        }

        if (aProperties.length == 0 && bProperties.length == 0) { // at least a special case for QUrl
            return eq && (JSON.stringify(act) == JSON.stringify(exp));
        }

        // Ensures identical properties name
        return eq && qtest_compareInternal(aProperties.sort(), bProperties.sort());

    }

    /*! \internal */
    function qtest_compareInternalArrays(actual, expected) {
        if (actual.length != expected.length) {
            return false
        }

        for (var i = 0, len = actual.length; i < len; i++) {
            if (!qtest_compareInternal(actual[i], expected[i])) {
                return false
            }
        }

        return true
    }


    /*!

//    /*
//        compare values and throws msg if lhs != rhs
//    */
    function compare(lhs, rhs, msg="") {
      let expfail = qmlbot.isExpectedToFail("")
      expfail = expfail ? expfail : null // true = xpassed, false = xpassed, null = usual
      let expfailmessage = ""
      if (expfail)
        {
        expfailmessage = qmlbot.getExpectedToFailMessage("")
        }
      let res = false
      res = qtest_compareInternal(lhs,rhs)
      if (res && expfail){  // exp fail but doesn't fail == xpassed
        expfail = false // turn from xfailed to xpassed
        msg = "compare returned TRUE unexpectedly"
        res = false // make it throw
      }
      if (!res)
        throw new U.CompareError(msg, {"lhs":lhs, "rhs":rhs, "expectFail":expfail,"expectFailMessage":expfailmessage})
      }

    /*
        createTemporaryObject
    */
    function createTemporaryObject(component, parent, properties={})  {
      if (component.status != 1) {
        throw new U.PytestError(`${component.errorString()}`)
      }
      let obj = component.createObject(parent, properties)

      temporaryObjects.push(obj)
      return obj
    }


   /*
       fail the current test with msg
   */
   function expectFail(tag, msg) {
        if (tag === undefined) {
            warn("tag argument missing from expectFail()")
            tag = ""
        }
        if (msg === undefined) {
            warn("message argument missing from expectFail()")
            msg = ""
        }
        qmlbot.addExpectToFail(tag, msg)
    }

    /*
        fail the current test with msg
    */
    function fail(msg) {
        if (msg === undefined)
            msg = "";
        throw new U.PytestError(msg)
    }

    /*
        finChild(parent, objectName)
        strict copy/pasted from QtTest/TestCase.qml from Pyside2.15
        except `qtest_results` change to `qmlbot`

    */
    function findChild(parent, objectName) {
        // First, search the visual item hierarchy.
        var child = qtest_findVisualChild(parent, objectName);
        if (child)
            return child;
        // If it's not a visual child, it might be a QObject child.
        return qmlbot.findChild(parent, objectName);
    }

    /*! strict copy pasted from QtTest/TestCase.qml form PySide2.15 */
    function qtest_findVisualChild(parent, objectName) {
        if (!parent || parent.children === undefined)
            return null;

        for (var i = 0; i < parent.children.length; ++i) {
            // Is this direct child of ours the child we're after?
            var child = parent.children[i];
            if (child.objectName === objectName)
                return child;
        }

        for (i = 0; i < parent.children.length; ++i) {
            // Try the direct child's children.
            child = qtest_findVisualChild(parent.children[i], objectName);
            if (child)
                return child;
        }
        return null;
    }



    /*
        init(): executed befrore each tests
    */
    function init() {

    }

    /*
        keyClick
    */
    function keyClick(key, modifiers = Qt.NoModifier, delay = -1) {
            qmlbot.keyEvent("keyClick", key, modifiers, delay)
    }

    /*
        keyPress
    */
    function keyPress(key, modifiers = Qt.NoModifier, delay = -1) {
            qmlbot.keyEvent("keyPress", key, modifiers, delay)
    }

    /*
        keyRelaase
    */
    function keyRelease(key, modifiers = Qt.NoModifier, delay = -1) {
            qmlbot.keyEvent("keyRelease", key, modifiers, delay)
    }

    /*
        keySequence
    */
    function keySequence(seq) {
            qmlbot.keySequence(seq)
    }



    /*
        mouseClick
    */
    function mouseClick(item, x = item.width / 2, y = item.height / 2, button = Qt.LeftButton, modifiers = Qt.NoModifier, delay = -1) {
            let point = item.mapToItem(Window.contentItem, x, y)
            qmlbot.mouseEvent("mouseClick", point, button, modifiers, delay)
    }
    /*
        mouseDoubleClickSequence
    */
    function mouseDoubleClickSequence(item, x = item.width / 2, y = item.height / 2, button = Qt.LeftButton, modifiers = Qt.NoModifier, delay = -1) {
            let point = item.mapToItem(Window.contentItem, x, y)
            qmlbot.mouseEvent("mouseDClick", point, button, modifiers, delay)
    }

    /*
        mouseMove
    */
    function mouseMove(item, x, y, delay=-1) {
            let point = item.mapToItem(Window.contentItem, x, y)
            qmlbot.mouseEvent("mouseMove", point, Qt.NoButton, Qt.NoModifier, delay)
    }

    /*
        mousePress
    */
    function mousePress(item, x = item.width / 2, y = item.height / 2, button = Qt.LeftButton, modifiers = Qt.NoModifier, delay = -1) {
            let point = item.mapToItem(Window.contentItem, x, y)
            qmlbot.mouseEvent("mousePress", point, button, modifiers, delay)
    }


    /*
        mouseRelease
    */
    function mouseRelease(item, x = item.width / 2, y = item.height / 2, button = Qt.LeftButton, modifiers = Qt.NoModifier, delay = -1) {
            let point = item.mapToItem(Window.contentItem, x, y)
            qmlbot.mouseEvent("mouseRelease", point, button, modifiers, delay)
    }


    /*
        Skip the current test

    */
    function skip(message="") {
        throw new U.SkipError(message)
    }

    /*
        tryCompare
    */
    function tryCompare(obj, prop, value, timeout, msg) {
        if (arguments.length == 1 || (typeof(prop) != "string" && typeof(prop) != "number")) {
            {
            throw new U.PyTestError("A property name as string or index is required for tryCompare")
            }
        }
        if (arguments.length == 2) {
            throw new U.PyTestError("A value is required for tryCompare")

        }
        if (timeout !== undefined && typeof(timeout) != "number") {
            throw new U.PyTestError("timeout should be a number")

        }
        if (!timeout)
            timeout = 5000
        if (msg === undefined)
            msg = "property " + prop
        if (!qtest_compareInternal(obj[prop], value))
            wait(0)
        var i = 0
        while (i < timeout ) {
                    if (qtest_compareInternal(obj[prop], value)){
                        break;
                    }
                    wait(50)
                    i += 50
                }
        compare(obj[prop], value, `tryCompare: property '${prop}' never got value '${value}'`)
     }

     /*
        Fails the current test case if function does not evaluate to true before the specified timeout (in milliseconds) has elapsed
      */
     function tryVerify(expressionFunction, timeout, msg) {
        if (!expressionFunction || !(expressionFunction instanceof Function)) {
            throw new U.PyTestError("First argument must be a function")
        }

        if (timeout && typeof(timeout) !== "number") {
            throw new U.PyTestError("timeout argument must be a number")
        }

        if (msg && typeof(msg) !== "string") {
            throw new U.PyTestError("message argument must be a string")
        }

        if (!timeout)
            timeout = 5000

        if (!expressionFunction())
            wait(0)

        var i = 0
        while (i < timeout && !expressionFunction()) {
            wait(50)
            i += 50
        }
        msg = msg ? msg : `tryVerify fonction never got true`
        compare(Boolean(expressionFunction()), true, msg)
    }
      /*
        verify that condition is true
      */
     function verify(condition, message="") {
        compare(Boolean(condition), true)
     }

    /*
        Non blocking-UI wait method.
    */
    function wait(ms) {
        qmlbot.wait(ms)
    }

     Component.onCompleted: {
        collectTests()
     }
}