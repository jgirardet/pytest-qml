import warnings
from typing import Any, Optional, Union

from pytestqml.qt import (
    QObject,
    Slot,
    QJSValue,
    Signal,
    Property,
    Qt,
    QPoint,
    QTest,
    QKeySequence,
    QUrl,
    QVector3D,
    QDateTime,
    QColor,
    QGuiApplication,
    QWheelEvent,
    QPointF,
    QWindow,
)
from pytestqt.qtbot import QtBot


class QmlBot(QObject):
    """
    Backend used in TestCase for various things.
    view: QQuickView
    settings: dict

    """

    def __init__(self, view: "TestView", settings={}):
        super().__init__()
        self.view = view
        self._settings = settings
        self.expectedToFail = {}
        # self.pressed_keys = set()

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

    @Slot(str, str)
    def addExpectToFail(self, tag: str, message: str):
        """
        tag: str =  test_name+tag
        message: str = message
        """
        self.expectedToFail[tag] = message

    @Slot("QVariant", "QVariant", result=int)
    def compare(self, lhs: Any, rhs: Any) -> bool:
        """
        Used in TestCase.compare for some corner cases
        return value:
            0: false
            1: true
            2: skip

        """
        if isinstance(lhs, QJSValue):
            lhs = lhs.toVariant()
        if isinstance(rhs, QJSValue):
            rhs = rhs.toVariant()
        if isinstance(lhs, QUrl) and isinstance(rhs, QUrl):  # QTBUG-61297
            return int(lhs == rhs)
        return 2

    @Property(int)
    def dragThreshold(self):
        app = QGuiApplication.instance()
        return app.styleHints().startDragDistance()

    @Slot(str, result=bool)
    def isExpectedToFail(self, tag: str):
        return tag in self.expectedToFail

    @Slot(str, result=str)
    def getExpectedToFailMessage(self, tag: str):
        return self.expectedToFail.pop(tag)

    @Slot(QObject, str, result=QObject)
    def findChild(self, parent: QObject, objectName: str) -> Optional[QObject]:
        if not parent:
            return
        return parent.findChild(QObject, objectName)

    @Slot("QVariant", "QVariant", float, result=bool)
    def fuzzyCompare(
        self,
        actual: Union[float, QColor],
        expected: Union[float, QColor],
        delta: float = 0.0,
    ) -> bool:
        """
        Compare actual and expected with delta accepted.
        """
        if isinstance(actual, bool) or isinstance(expected, bool):
            return False

        if isinstance(actual, float) and isinstance(expected, float):
            return abs(actual - expected) <= delta

        try:
            actual = QColor(actual)
            expected = QColor(expected)
        except TypeError:
            return False
        if actual.isValid() and expected.isValid():
            return (
                abs(actual.green() - expected.green()) <= delta
                and abs(actual.red() - expected.red()) <= delta
                and abs(actual.blue() - expected.blue()) <= delta
                and abs(actual.blue() - expected.blue()) <= delta
                and abs(actual.alpha() - expected.alpha()) <= delta
            )
        return False

    @Slot(str, QPoint, int, int, int, QObject)
    def mouseEvent(
        self,
        action: str,
        point: QPoint,
        button: int,
        modifiers: int,
        delay: int,
        rootitem: QObject,
    ):
        window = self._get_window(rootitem)
        if not window:
            raise ValueError("no window found for this element")
        if action == "mouseMove":
            QTest.mouseMove(window, point, delay)
        else:
            # Conversion needed for pyqt5/pyside2 compat
            modifiers = Qt.KeyboardModifier(modifiers)
            button = Qt.MouseButton(button)
            getattr(QTest, action)(window, button, modifiers, point, delay)

    @Slot(QPointF, QPointF, QPoint, int, int, int, QObject)
    def mouseWheel(
        self, pos, globalPos, angleDelta, buttons, modifiers, delay, rootitem: QObject
    ):

        window = self._get_window(rootitem)
        if not window:
            raise ValueError("no window found for this element")
        modifiers = Qt.KeyboardModifier(modifiers)
        buttons = Qt.MouseButton(buttons)
        pixelDelta = QPoint()
        phase = Qt.NoScrollPhase
        inverted = False
        source = Qt.MouseEventNotSynthesized

        event = QWheelEvent(
            pos,
            globalPos,
            pixelDelta,
            angleDelta,
            buttons,
            modifiers,
            phase,
            inverted,
            source,
        )
        if delay > 0:
            self.wait(delay)
        QGuiApplication.instance().postEvent(window, event)
        QGuiApplication.instance().processEvents()

    @Slot(str, int, int, int)
    def keyEvent(
        self,
        action: str,
        key: int,
        modifiers: int = None,
        delay: int = None,
    ):
        # Conversion needed for pyqt5/pyside2 compat
        # print(modifiers)
        key = Qt.Key(key)
        modifiers = Qt.KeyboardModifiers(modifiers)
        window = self.view.app.focusWindow() or self.view
        getattr(QTest, action)(window, key, modifiers, delay)

    @Slot(str)
    def keySequence(self, seq: str):
        window = self.view.app.focusWindow() or self.view
        QTest.keySequence(window, QKeySequence(seq))

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

    @Slot(str)
    def warn(self, value: str):
        warnings.warn_explicit(value, QMLWarning, "", 0)

    #
    # @Slot("QVariant", result=str)
    # def stringify(self, value: Any):
    #     result: str = ""
    #     if value.isObject():
    #         v = value.toVariant()
    #         if v.isValid():
    #             v = value.toVariant()
    #             if isinstance(v, QVector3D):
    #                 result = f"Qt.Vector3d({v.x()}, {v.y()}, {v.z()})"
    #             elif isinstance(v, QUrl):
    #                 result = f"Qt.url({v.toString()})"
    #             elif isinstance(v, QDateTime):
    #                 result = v.toString(Qt.ISODateWithMs)
    #             else:
    #                 result = v.toString()
    #         else:
    #             result = "Object"
    #
    #     if not result:
    #         if value.isArray():
    #             result += str(value.toVariant())
    #         else:
    #             result += str(value)
    #     return result
    #

    """
    Private api
    """

    # def _event_handler(self):
    #     window = self.engine.rootObjects()[0]
    #     QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, QPoint(20, 10), 0)
    # def _track_key(self, key):
    def _get_window(self, rootitem: QObject) -> QWindow:
        for win in self.view.app.allWindows():
            if win.contentItem() == rootitem:
                return win


class QMLWarning(UserWarning):
    pass
