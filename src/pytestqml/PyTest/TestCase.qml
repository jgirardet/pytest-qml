import QtQuick 2.0
import "utils.mjs" as U
import QtQuick.Window 2.2

Item {
        id: root

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
//        onWindowShownChanged: qmlbot.debug("changed"+windowShown)

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
            return res
////
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
            error.stask  = cleanupErr.stack
            res = error.toObj()
            qmlbot.debug(res)
        }
        result = res
        running=false
        testCompleted()
        return res
    }

    /*
        compare values and throws msg if lhs != rhs
    */
    function compare(lhs, rhs, msg="") {
      let res = false
      if (typeof lhs === typeof rhs){
        res = qmlbot.compare(lhs, rhs)
        }
      if (!res)
        throw new U.CompareError(msg, {"lhs":lhs, "rhs":rhs})
      }

    /*
        createTemporaryObject

        See cleanup for differences with C++/QT
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
    function fail(msg) {
        if (msg === undefined)
            msg = "";
        qtest_results.fail(msg, util.callerFile(), util.callerLine())
        throw new Error("QtQuickTest::fail")
    }

    /*
        init(): executed befrore each tests
    */
    function init() {

    }


    /*
        cleanup the current test

        Not so useful as C++/Qt implementation since each test is run
        independently so everything wil be destroyed after the test, whatever happen.

    */
    function cleanup() {
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
            throw new U.PyTestError("A property name as string or index is required for tryCompare", {"aaa":"azer"})
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
        if (!qmlbot.compare(obj[prop], value))
            wait(0)
        var i = 0
        while (i < timeout ) {
                    if (qmlbot.compare(obj[prop], value)){
                        break;
                    }
                    wait(50)
                    i += 50
                }
        compare(obj[prop], value, `tryCompare: property '${prop}' never got value '${value}'`)
     }

      /*
        verify that condition is true
      */
     function verify(condition, message="") {
        compare(condition, true)
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