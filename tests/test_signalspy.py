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
