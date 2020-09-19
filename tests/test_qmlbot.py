from time import sleep, time

import pytest
from pytestqml.qmlbot import QmlBot
from pytestqml.qt import QObject, Signal, QJSValue, QQuickView
from pytestqt.exceptions import TimeoutError


@pytest.fixture
def bot(qtbot) -> QmlBot:
    return QmlBot(QQuickView())


def test_init(bot):
    assert isinstance(bot, (QmlBot, QObject))


def test_wait_signal(bot:QmlBot, qtbot):
    class Some(QObject):
        asig = Signal()
    s=Some()

    # error
    with pytest.raises(TimeoutError):
        with bot.wait_signal(s.asig, timeout=20, raising=True):
            pass

    # error no raise
    d1=time()
    with bot.wait_signal(s.asig, timeout=200, raising=False):
        a=1
    d2=time()
    delta = (d2-d1)*1000
    assert pytest.approx(200, delta, 20)


    # pass
    with bot.wait_signal(s.asig, timeout=20, raising=True):
        s.asig.emit()

"""
Test des Slots
"""

def test_debug(bot, capsys):
    bot.debug(1)
    assert capsys.readouterr().out == "1"+"\n"
    bot.debug("1")
    assert capsys.readouterr().out == "1"+"\n"

    v = QQuickView()
    value = v.engine().newArray(3)
    value.setProperty(0,1)
    value.setProperty(1,2)
    value.setProperty(2,3)
    bot.debug(value)
    assert capsys.readouterr().out == "[1, 2, 3]"+"\n"

    v = QQuickView()
    value = v.engine().newObject()
    value.setProperty("aa","aaa")
    value.setProperty("bb","bbb")
    bot.debug(value)
    assert capsys.readouterr().out == "{'aa': 'aaa', 'bb': 'bbb'}"+"\n"

def test_wait(bot):
    d1 = time()
    bot.wait(0)
    d2 = time()
    delta = (d2-d1)*1000
    assert delta < 0.1
    d1 = time()
    bot.wait(100)
    d2 = time()
    delta = (d2-d1)*1000
    assert delta == pytest.approx(100, 10)

def test_compare():
    pass # tested in test_TestCase.py

def test_windowShown(bot: QmlBot, qtbot):
    assert not bot.windowShown
    bot.view.show()
    qtbot.wait_until(lambda: bot.view.isExposed())
    assert bot.windowShown

def test_settings(bot: QmlBot):
    assert bot._settings == {}
    bot._settings = {"string":"2", "int":2}
    assert bot.settings("string") == "2"
    assert bot.settings("int") == 2
# def test_windowShownTimeout(bot