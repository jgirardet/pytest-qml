from time import sleep, time

import pytest
from pytestqml.qmlbot import QmlBot
from pytestqml.qt import QObject, Signal, QJSValue, QQuickView, QColor
from pytestqt.exceptions import TimeoutError


@pytest.fixture
def bot(qtbot) -> QmlBot:
    return QmlBot(QQuickView())


def test_init(bot):
    assert isinstance(bot, (QmlBot, QObject))


def test_wait_signal(bot: QmlBot, qtbot):
    class Some(QObject):
        asig = Signal()

    s = Some()

    # error
    with pytest.raises(TimeoutError):
        with bot.wait_signal(s.asig, timeout=20, raising=True):
            pass

    # error no raise
    d1 = time()
    with bot.wait_signal(s.asig, timeout=200, raising=False):
        a = 1
    d2 = time()
    delta = (d2 - d1) * 1000
    assert pytest.approx(200, delta, 20)

    # pass
    with bot.wait_signal(s.asig, timeout=20, raising=True):
        s.asig.emit()


"""
Test des Slots
"""


def test_debug(bot, capsys):
    bot.debug(1)
    assert capsys.readouterr().out == "1" + "\n"
    bot.debug("1")
    assert capsys.readouterr().out == "1" + "\n"

    v = QQuickView()
    value = v.engine().newArray(3)
    value.setProperty(0, 1)
    value.setProperty(1, 2)
    value.setProperty(2, 3)
    bot.debug(value)
    assert capsys.readouterr().out == "[1, 2, 3]" + "\n"

    v = QQuickView()
    value = v.engine().newObject()
    value.setProperty("aa", "aaa")
    value.setProperty("bb", "bbb")
    bot.debug(value)
    assert capsys.readouterr().out == "{'aa': 'aaa', 'bb': 'bbb'}" + "\n"


def test_wait(bot):
    d1 = time()
    bot.wait(100)
    d2 = time()
    delta = (d2 - d1) * 1000
    assert delta == pytest.approx(100, 10)


def test_windowShown(bot: QmlBot, qtbot):
    assert not bot.windowShown
    bot.view.show()
    qtbot.wait_until(lambda: bot.view.isExposed())
    assert bot.windowShown


def test_settings(bot: QmlBot):
    assert bot._settings == {}
    bot._settings = {"string": "2", "int": 2}
    assert bot.settings("string") == "2"
    assert bot.settings("int") == 2


def test_mouseEvent():
    pass  # tested in test_TestCase.py


@pytest.mark.parametrize(
    "lhs, rhs, delta,res",
    [
        (True, True, None, False),  # won't compare anything else
        (0.123, 0.12, 0.01, True),
        (0.123, 0.12, 0.001, False),
        (QColor("#ff0000"), QColor("red"), 0, True),
        (
            QColor.fromRgbF(1.000000, 0.000000, 0.99, 1.000000),
            QColor.fromRgbF(1.000000, 0.000000, 1, 1.000000),
            5,
            True,
        ),
        (
            QColor.fromRgbF(1.000000, 0.000000, 1, 1.000000),
            QColor.fromRgbF(1.000000, 0.000000, 0.99, 1.000000),
            0,
            False,
        ),
        (
            QColor.fromRgbF(1.000000, 0.01, 1, 1.000000),
            QColor.fromRgbF(1.000000, 0.000000, 1, 1.000000),
            5,
            True,
        ),
        (
            QColor.fromRgbF(0.99, 0, 1, 1.000000),
            QColor.fromRgbF(1.000000, 0.000000, 1, 1.000000),
            5,
            True,
        ),
        (
            QColor.fromRgbF(1, 0, 1, 0.99),
            QColor.fromRgbF(1.000000, 0.000000, 1, 1.000000),
            5,
            True,
        ),
    ],
)
def test_fuzzyCompare(bot, lhs, rhs, delta, res):
    assert bot.fuzzyCompare(lhs, rhs, delta) == res
