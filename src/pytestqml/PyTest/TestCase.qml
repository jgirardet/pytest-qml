import QtQuick 2.0
import "errors.mjs" as Err
import "qtest.mjs" as Qtest
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
            All collected tests of this TestCase
            collected = {"testName":test_function}
        */
        property var data_func_collected: ({})

        /*
            TestCase completed
        */
        property bool completed: false

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
        function collect_from_data(func, key, value) {
            let datas = func()
                for (const [i,data] of datas.entries()) {
                    // use "tag" if exists or index to name the function
                    // will be : test_myfunc_tagname or test_myfunc_index (index is 0,1...)
                    let name  = data.tag ? key+ "_"+ data.tag : key+"_"+i
                    collected[name] = {"fn":value, "args": data}
                }
        }

        // First loop search for "data" function
        for (const [key, value] of Object.entries(root)){
            if (typeof value == "function" && key.endsWith("_data")) {
                  data_func_collected[key.slice(0,-5)] = value
            }
        }

        // Second loop search for tests
        for (const [key, value] of Object.entries(root)){
          // keep only test functions
          if (typeof value == "function" && key.startsWith("test_")){
            // skip if "data" function
            if (typeof value == "function" && key.endsWith("_data")) {
                continue
            }
            // check if a data function exists
            if (key in data_func_collected) {
                collect_from_data(data_func_collected[key], key, value)
            }
            // take data from "init_data
            else if ("init_data" in root) {
                collect_from_data(init_data, key,value)
            // No data
            } else {
              collected[key] = {"fn":value,"args":undefined}
            }
          }
        }
     }

     function runOneTest(testName) {
        running=true
        let res= {}
        try {
          init()
          let theTest = collected[testName]
          if (typeof theTest.args != "undefined" && theTest.fn.length==0){
            // data was not added to test_function parameter
            warn("no data supplied for " + testName)
          }
          theTest.fn(theTest.args)
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
            for(const obj of temporaryObjects){
            obj.destroy()
            }

            temporaryObjects = []
        } catch (cleanupErr) {
            let error = new Err.CleanupError(cleanupErr.message, {"other":res})
            error.stack  = cleanupErr.stack
            res = error.toObj()
            qmlbot.debug(res)
        }
        result = res
        running=false
        delete collected[testName]
        if (Object.keys(collected).length==0){
            cleanupTestCase()
            completed=true
        }
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

    /*
        cleanupTestCase
    */
    function cleanupTestCase() {
    }






//    /*
//        compare values and throws msg if lhs != rhs
//    */
    function compare(lhs, rhs, msg="") {
      let expfail = qmlbot.isExpectedToFail("")
      expfail = expfail ? expfail : null // true = xfail, false = xpassed, null = usual
      let expfailmessage = ""
      if (expfail)
        {
        expfailmessage = qmlbot.getExpectedToFailMessage("")
        }
      let res = false
      res = Qtest.qtest_compareInternal(lhs,rhs)
      if (res && expfail){  // exp fail but doesn't fail == xpassed
        expfail = false // turn from xfailed to xpassed
        msg = "compare returned TRUE unexpectedly"
        res = false // make it throw
      }
      if (!res)
        throw new Err.CompareError(msg, {"lhs":lhs, "rhs":rhs, "expectFail":expfail,"expectFailMessage":expfailmessage})
      }

    /*
        createTemporaryObject
    */
    function createTemporaryObject(component, parent, properties={})  {
      if (component.status != 1) {
        throw new Err.PytestError(`${component.errorString()}`)
      }
      let obj = component.createObject(parent, properties)

      temporaryObjects.push(obj)
      return obj
    }

    /*
        createTemporaryObject
    */
    function createTemporaryQmlObject(qml, parent, filePath) {
        if (typeof qml !== "string") {
            throw new Err.PytestError("First argument must be a string of QML; actual type is " + typeof qml)
        }

        if (!parent || typeof parent !== "object") {
            throw new Err.PytestError("Second argument must be a valid parent object; actual type is " + typeof parent)
        }

        if (filePath !== undefined && typeof filePath !== "string") {
            throw new Err.PytestError("Third argument must be a file path string; actual type is " + typeof filePath)
        }

        var object = Qt.createQmlObject(qml, parent, filePath);
        temporaryObjects.push(object);
        return object;
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
        throw new Err.PytestError(msg)
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
        fuzzyCompare(actual, expected, delta)
   */
   function fuzzyCompare(actual, expected, delta, msg) {
        if (delta === undefined)
            throw new Err.PyTestError("A delta value is required for fuzzyCompare")

//        var success =
//
        if (!qmlbot.fuzzyCompare(actual, expected, delta)){
            if (msg === undefined)
                msg = `with delta=${delta}`
            throw new Err.CompareError(msg, {"lhs":actual, "rhs":expected})//, "expectFail":null,"expectFailMessage":""})
        }
    }

    /*
        init(): executed befrore each tests
    */
    function init() {
    }

    /*
        initTestCase(): executed before any other function
    */
    function initTestCase() {
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
    function mouseClick(item, x, y, button, modifiers, delay) {
            qtest_verifyItem(item, "mouseClick")
            if (button === undefined)
                button = Qt.LeftButton
            if (modifiers === undefined)
                modifiers = Qt.NoModifier
            if (delay == undefined)
                delay = -1
            if (x === undefined)
                x = item.width / 2
            if (y === undefined)
                y = item.height / 2
            let [point, rootitem] = _getCoordInWindow(item,x, y)
            qmlbot.mouseEvent("mouseClick", point, button, modifiers, delay, rootitem)
    }
    /*
        mouseDoubleClickSequence
    */
    function mouseDoubleClickSequence(item, x, y, button, modifiers, delay) {
            qtest_verifyItem(item, "mouseDoubleClickSequence")
            if (button === undefined)
            button = Qt.LeftButton
            if (modifiers === undefined)
                modifiers = Qt.NoModifier
            if (delay == undefined)
                delay = -1
            if (x === undefined)
                x = item.width / 2
            if (y === undefined)
                y = item.height / 2
            let [point, rootitem] = _getCoordInWindow(item,x, y)
            qmlbot.mouseEvent("mouseDClick", point, button, modifiers, delay, rootitem)
    }

    /*
        MouseDrag(item,x, y, dx, dy, button, modifiers, delay)
        almost copy pasted from PySide2 5.15.1
    */
    function mouseDrag(item, x, y, dx, dy, button, modifiers, delay) {
        qtest_verifyItem(item, "mouseDrag")

        if (item.x === undefined || item.y === undefined)
            return
        if (button === undefined)
            button = Qt.LeftButton
        if (modifiers === undefined)
            modifiers = Qt.NoModifier
        if (delay == undefined)
            delay = -1
        // we fix qtest_events.defaultMouseDelay to 0 (the case or defautEventDelay)
        var moveDelay = Math.max(1, delay === -1 ? 0 : delay)

        // Divide dx and dy to have intermediate mouseMove while dragging
        // Fractions of dx/dy need be superior to the dragThreshold
        // to make the drag works though
        var intermediateDx = Math.round(dx/3)
        if (Math.abs(intermediateDx) < (qmlbot.dragThreshold + 1))
            intermediateDx = 0
        var intermediateDy = Math.round(dy/3)
        if (Math.abs(intermediateDy) < (qmlbot.dragThreshold + 1))
            intermediateDy = 0

        mousePress(item, x, y, button, modifiers, delay)

        // Trigger dragging by dragging past the drag threshold, but making sure to only drag
        // along a certain axis if a distance greater than zero was given for that axis.
        var dragTriggerXDistance = dx > 0 ? (qmlbot.dragThreshold + 1) : 0
        var dragTriggerYDistance = dy > 0 ? (qmlbot.dragThreshold + 1) : 0
        mouseMove(item, x + dragTriggerXDistance, y + dragTriggerYDistance, moveDelay, button)
        if (intermediateDx !== 0 || intermediateDy !== 0) {
            mouseMove(item, x + intermediateDx, y + intermediateDy, moveDelay, button)
            mouseMove(item, x + 2*intermediateDx, y + 2*intermediateDy, moveDelay, button)
        }
//        mouseMove(item, x + dx, y + dy, moveDelay, button) // doesnt work  with it... why ? qttest and self test
        mouseRelease(item, x + dx, y + dy, button, modifiers, delay)
    }


    /*
        mouseMove
    */
    function mouseMove(item, x, y, delay, buttons) {
            qtest_verifyItem(item, "mouseMove")
            if (delay == undefined)
                delay = -1
            if (buttons == undefined)
                buttons = Qt.NoButton
            let [point, rootitem] = _getCoordInWindow(item,x, y)
            qmlbot.mouseEvent("mouseMove", point, buttons, Qt.NoModifier, delay, rootitem)
    }

    /*
        mousePress
    */
    function mousePress(item, x, y, button, modifiers, delay) {
            qtest_verifyItem(item, "mousePress")
            if (button === undefined)
            button = Qt.LeftButton
            if (modifiers === undefined)
                modifiers = Qt.NoModifier
            if (delay == undefined)
                delay = -1
            if (x === undefined)
                x = item.width / 2
            if (y === undefined)
                y = item.height / 2
                print(Window.contentItem)
            let [point, rootitem] = _getCoordInWindow(item,x, y)
            qmlbot.mouseEvent("mousePress", point, button, modifiers, delay, rootitem)
    }


    /*
        mouseRelease
    */
    function mouseRelease(item, x, y, button, modifiers, delay) {
            qtest_verifyItem(item, "mouseRelease")
            if (button === undefined)
            button = Qt.LeftButton
            if (modifiers === undefined)
                modifiers = Qt.NoModifier
            if (delay == undefined)
                delay = -1
            if (x === undefined)
                x = item.width / 2
            if (y === undefined)
                y = item.height / 2
            let [point, rootitem] = _getCoordInWindow(item,x, y)
            qmlbot.mouseEvent("mouseRelease", point, button, modifiers, delay, rootitem)
    }

    /*
        MouseWheel
    */
    function mouseWheel(item, x, y, xDelta, yDelta, buttons, modifiers, delay) {
        qtest_verifyItem(item, "mouseWheel")
        if (delay == undefined)
            delay = -1
        if (buttons == undefined)
            buttons = Qt.NoButton
        if (modifiers === undefined)
            modifiers = Qt.NoModifier
        if (xDelta == undefined)
            xDelta = 0
        if (yDelta == undefined)
            yDelta = 0
        let [pos, rootitem] = _getCoordInWindow(item,x, y)
        let globalPos = item.mapToGlobal(x, y)
        let delta = Qt.point(xDelta, yDelta)
        qmlbot.mouseWheel(pos, globalPos, delta, buttons, modifiers, delay, rootitem)
   }


    /*
        Skip the current test

    */
    function skip(message="") {
        throw new Err.SkipError(message)
    }

    /*
        tryCompare
    */
    function tryCompare(obj, prop, value, timeout, msg) {
        if (arguments.length == 1 || (typeof(prop) != "string" && typeof(prop) != "number")) {
            {
            throw new Err.PyTestError("A property name as string or index is required for tryCompare")
            }
        }
        if (arguments.length == 2) {
            throw new Err.PyTestError("A value is required for tryCompare")

        }
        if (timeout !== undefined && typeof(timeout) != "number") {
            throw new Err.PyTestError("timeout should be a number")

        }
        if (!timeout)
            timeout = 5000
        if (msg === undefined)
            msg = "property " + prop
        if (!Qtest.qtest_compareInternal(obj[prop], value))
            wait(0)
        var i = 0
        while (i < timeout ) {
                    if (Qtest.qtest_compareInternal(obj[prop], value)){
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
            throw new Err.PyTestError("First argument must be a function")
        }

        if (timeout && typeof(timeout) !== "number") {
            throw new Err.PyTestError("timeout argument must be a number")
        }

        if (msg && typeof(msg) !== "string") {
            throw new Err.PyTestError("message argument must be a string")
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

    function warn(msg) {
        qmlbot.warn(msg)
    }




     Component.onCompleted: {
        collectTests()
        initTestCase()
     }

    function _findRootItem(item) {
      let p = item
      while (true) {
                if (p.parent)
                   p = p.parent
                else
                   break;
            }
      return p
   }


   function _getCoordInWindow(item, x, y) {
        let rootitem = _findRootItem(item)
        let point = item.mapToItem(rootitem, x, y)
        return [point, rootitem]

   }

    function qtest_compareInternal(act,exp) {
        // needed by qttestsuite
        return Qtest.qtest_compareInternal(act,exp)
        }

    /*
    Qtest Functions copy pasted expect error managment
    */

    /*! \internal */
    function qtest_verifyItem(item, method) {
        try {
            if (!(item instanceof Item) &&
                !(item instanceof Window)) {
                // it's a QObject, but not a type
                throw new Err.PyTestError("TypeError: %1 requires an Item or Window type".arg(method), 2);
            }
        } catch (e) { // it's not a QObject
            throw new Err.PyTestError("TypeError: %1 requires an Item or Window type".arg(method), 3);
        }

        return true;
}


}