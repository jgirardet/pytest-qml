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
    assert qt.QtQuick.QQuickView
    assert qt.Property.read
    assert qt.Slot
    assert qt.QPoint.x
    assert qt.Signal
    assert qt.QQuickView
    assert qt.QObject
    assert qt.QtTest.QTest
    assert qt.QColor.rgba
    assert qt.QJSValue.toVariant
