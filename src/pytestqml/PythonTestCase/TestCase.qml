import QtQuick 2.0
import "utils.mjs" as U

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



        onTestToRunChanged:{
            try {
           qmlbot.debug(["debug"], qmlbot.settings("whenTimeout"))
            tryCompare(root, "when", true, qmlbot.settings("whenTimeout"))
            } catch(err) {
            result = err.toObj()
            running=false
            testCompleted()
            return res
////
         }
//        cleanTemporaryObjects()
//        showOneLineResult(oneTest.testName, (res ? false : true))

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
//          init()
          collected[testName]()
            }
        catch (err){
           res=err.toObj()
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
        fail the current test with msg
    */
    function fail(msg) {
        if (msg === undefined)
            msg = "";
        qtest_results.fail(msg, util.callerFile(), util.callerLine())
        throw new Error("QtQuickTest::fail")
    }


    /*
        Non blocking-UI wait method.
    */
    function wait(ms) {
        qmlbot.wait(ms)
    }

    /*
        tryCompare
    */
    function tryCompare(obj, prop, value, timeout, msg) {
//    function tryCompare(obj, prop, value, timeout, msg) {
        qmlbot.debug(["entree dans trycompare", prop])
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
                        qmlbot.debug(obj)
                        break;
                    }
                    wait(50)
                    i += 50
                }
        compare(obj[prop], value, `tryCompare: property '${prop}' never got value '${value}'`)
     }

     function verify(condition, message="") {
        compare(condition, true)
     }


     Component.onCompleted: {
        collectTests()
     }
}