/****************************************************************************
* Large parts of the following code is taken from SignalSpy.qml of PySide2
*from Qt Company. See the orignal file for the license.
****************************************************************************/

import QtQuick 2.0
import "errors.mjs" as Err
import PyTest 1.0



Item {
    id: spy
    visible: false

    // Public API.
    /*!
        \qmlproperty object SignalSpy::target
        This property defines the target object that will be used to
        listen for emissions of the \l signalName signal.
        \sa signalName, count
    */
    property var target: null
    /*!
        \qmlproperty string SignalSpy::signalName
        This property defines the name of the signal on \l target to
        listen for.
        \sa target, count
    */
    property string signalName: ""
    /*!
        \qmlproperty int SignalSpy::count
        This property defines the number of times that \l signalName has
        been emitted from \l target since the last call to clear().
        \sa target, signalName, clear()
        \readonly
    */
    property alias count: spy.qtest_count
    /*!
        \qmlproperty bool SignalSpy::valid
        This property defines the current signal connection status. It will be true when the \l signalName of the \l target is connected successfully, otherwise it will be false.
        \sa count, target, signalName, clear()
        \readonly
    */
    property alias valid:spy.qtest_valid
    /*!
        \qmlproperty list SignalSpy::signalArguments
        This property holds a list of emitted signal arguments. Each emission of the signal will append one item to the list, containing the arguments of the signal.
        When connecting to a new \l target or new \l signalName or calling the \l clear() method, the \l signalArguments will be reset to empty.
        \sa signalName, clear()
        \readonly
    */
    property alias signalArguments:spy.qtest_signalArguments

    /*!
        \qmlmethod SignalSpy::clear()
        Clears \l count to 0, resets \l valid to false and clears the \l signalArguments to empty.
        \sa count, wait()
    */
    function clear() {
        qtest_count = 0
        qtest_expectedCount = 0
        qtest_signalArguments = []
    }

    /*!
        \qmlmethod SignalSpy::wait(timeout = 5000)
        Waits for the signal \l signalName on \l target to be emitted,
        for up to \a timeout milliseconds.  The test case will fail if
        the signal is not emitted.
        \code
        SignalSpy {
            id: spy
            target: button
            signalName: "clicked"
        }
        function test_async_click() {
            ...
            // do something that will cause clicked() to be emitted
            ...
            spy.wait()
            compare(spy.count, 1)
        }
        \endcode
        There are two possible scenarios: the signal has already been
        emitted when wait() is called, or the signal has not yet been
        emitted.  The wait() function handles the first scenario by immediately
        returning if the signal has already occurred.
        The clear() method can be used to discard information about signals
        that have already occurred to synchronize wait() with future signal
        emissions.
        \sa clear(), TestCase::tryCompare()
    */
    function wait(timeout) {
        if (timeout === undefined)
            timeout = 5000
        var expected = ++qtest_expectedCount
        var i = 0
        while (i < timeout && qtest_count < expected) {
            qmlbot.wait(50)
            i += 50
        }
        var success = (qtest_count >= expected)
        if (!success)
            throw new Err.PyTestError(`signal ${signalName} emitted ${qtest_count} times but ${expected}  was expected`)
//        if (!qtest_results.verify(success, "wait for signal " + signalName, util.callerFile(), util.callerLine()))
//            throw new Error("QtQuickTest::fail")
    }

    // Internal implementation detail follows.


    onTargetChanged: {
        qtest_update()
    }
    onSignalNameChanged: {
        qtest_update()
    }

    /*! \internal */
    property var qtest_prevTarget: null
    /*! \internal */
    property string qtest_prevSignalName: ""
    /*! \internal */
    property int qtest_expectedCount: 0
    /*! \internal */
    property var qtest_signalArguments:[]
    /*! \internal */
    property int qtest_count: 0
    /*! \internal */
    property bool qtest_valid:false
    /*! \internal */

    /*! \internal */
    function qtest_update() {
        if (qtest_prevTarget != null) {
            var prevHandlerName = qtest_signalHandlerName(qtest_prevSignalName)
            var prevFunc = qtest_prevTarget[prevHandlerName]
            if (prevFunc)
                prevFunc.disconnect(spy.qtest_activated)
            qtest_prevTarget = null
            qtest_prevSignalName = ""
        }
        if (target != null && signalName != "") {
            // Look for the signal name in the object
            var func = target[signalName]
            if (typeof func !== "function") {
                // If it is not a function, try looking for signal handler
                // i.e. (onSignal) this is needed for cases where there is a property
                // and a signal with the same name, e.g. Mousearea.pressed
                func = target[qtest_signalHandlerName(signalName)]
            }
            if (func === undefined) {
                spy.qtest_valid = false
                console.log("Signal '" + signalName + "' not found")
            } else {
                qtest_prevTarget = target
                qtest_prevSignalName = signalName
                func.connect(spy.qtest_activated)
                spy.qtest_valid = true
                spy.qtest_signalArguments = []
            }
        } else {
            spy.qtest_valid = false
        }
    }

    /*! \internal */
    function qtest_activated() {
        ++qtest_count
        spy.qtest_signalArguments[spy.qtest_signalArguments.length] = arguments
    }

    /*! \internal */
    function qtest_signalHandlerName(sn) {
        if (sn.substr(0, 2) === "on" && sn[2] === sn[2].toUpperCase())
            return sn
        return "on" + sn.substr(0, 1).toUpperCase() + sn.substr(1)
    }

}