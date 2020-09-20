from typing import Any

from PySide2.QtTest import QTest
from pytestqml.qt import (
    QObject,
    Slot,
    QtCore,
    QtGui,
    QJSValue,
    Signal,
    Property,
    QPointF,
    Qt,
    QPoint,
)
from pytestqt.qtbot import QtBot
from pytestqt.wait_signal import MultiSignalBlocker


class QmlBot(QObject):
    """
    Backend used in TestCase for various things.
    view: QQuickView
    settings: dict

    """

    def __init__(self, view, settings={}):
        super().__init__()
        self.view = view
        self._settings = settings

    def wait_signal(
        self,
        signal=None,
        timeout=1000,
        raising=None,
        check_params_cb=None,
    ):
        self._should_raise = lambda x: x  # qtbot hack
        return QtBot.wait_signal(
            self,
            signal=signal,
            timeout=timeout,
            raising=raising,
            check_params_cb=check_params_cb,
        )

    """
    Slots are used in PyTest. they should not be called directly but via a method of PyTest.qml
    
    """

    @Slot("QVariant")
    def debug(self, value: Any):
        if isinstance(value, QJSValue):
            value = value.toVariant()
        print(value)

    @Slot("QVariant", "QVariant", result=bool)
    def compare(self, lhs: Any, rhs: Any) -> bool:
        """
        Used in TestCase.compare.
        It assumes lhs, rhs are of the same type.

        """
        if isinstance(lhs, QJSValue):
            lhs = lhs.toVariant()
        if isinstance(rhs, QJSValue):
            rhs = rhs.toVariant()
        return lhs == rhs

    @Slot(float, float, int, int, int)
    def mousePress(self, x: float, y: float, button: int, modifiers: int, delay: float):
        # window = self.view.engine().rootObjects()[0]
        print("mouseprese")
        QTest.mousePress(self.view, Qt.LeftButton, Qt.NoModifier, QPoint(8, 11), 0)

    windowShownChanged = Signal()

    @Property(bool, notify=windowShownChanged)
    def windowShown(self) -> bool:
        return self.view.isExposed()

    @Slot(int)
    def wait(self, ms: int) -> None:
        """
        Non UI Blocking wait
        """
        QtBot.wait(self, ms)

    @Slot(str, result=int)
    def settings(self, key: str, value: Any = None):
        return self._settings[key]

    @Slot(str, "QVariant")
    def setSettings(self, key: str, value: Any):
        if isinstance(value, QJSValue):
            value = value.toVariant()
        self._settings[key] = value

    """
    Private api
    """

    # def _event_handler(self):
    #     window = self.engine.rootObjects()[0]
    #     QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, QPoint(20, 10), 0)
