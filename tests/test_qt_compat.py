import os
import pytest


def test_qt_api():
    from pytestqml.qt import qtapi

    if "pyside" in os.environ["TOX_ENV_NAME"]:
        assert qtapi == "PySide2"
    else:
        assert qtapi == "PyQt5"


def test_qt_api():
    "module is if content is present"
    from pytestqml import qt

    assert qt.QtCore.QEventLoop
    assert qt.QtGui.QColor
    assert qt.QGuiApplication
    assert qt.QWheelEvent
    assert qt.QWindow
    assert qt.QtQuick.QQuickView
    assert qt.Property.read
    assert qt.Slot
    assert qt.QUrl
    assert qt.QDateTime
    assert qt.QPoint.x
    assert qt.QPointF.x
    assert qt.Qt.LeftButton
    assert qt.QEventLoop.exec_
    assert qt.Signal
    assert qt.QQuickView
    assert qt.QVector3D
    assert qt.QKeySequence
    assert qt.QObject
    assert qt.QtTest.QTest
    assert qt.QTest
    assert qt.QColor.rgba
    assert qt.QJSValue.toVariant
    assert qt.QQmlEngine.clearComponentCache
    assert qt.qmlRegisterType
