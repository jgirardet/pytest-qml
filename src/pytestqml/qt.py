from importlib import import_module
from typing import Optional

try:
    import PySide2
except ImportError:
    try:
        import PyQt5
    except ImportError:
        raise ImportError("PySide2 ou PyQt5 should be installed")
    else:
        qtapi = "PyQt5"
else:
    qtapi = "PySide2"

PYSIDE2 = qtapi == "PySide2"
PYQT5 = qtapi == "PyQt5"

QtCore = None  # type: PySide2.QtCore
QtGui = None  # type: PySide2.QtGui
QtQuick = None  # type: PySide2.QtQuick
QtTest = None  # type: PySide2.QtTest
QtQml = None  # type: PySide2.QtQml


COMMON = ["QtCore", "QtGui", "QtQuick", "QtTest", "QtQml"]
for module in COMMON:
    key = module.split(".")[-1]
    vars()[module] = import_module(".".join((qtapi, module)))

QEventLoop = QtCore.QEventLoop  # type: PySide2.QtCore.QEventLoop
QObject = QtCore.QObject  # type: PySide2.QtCore.QObject
QPoint = QtCore.QPoint  # type: PySide2.QtCore.QPoint
QPointF = QtCore.QPointF  # type: PySide2.QtCore.QPointF
Qt = QtCore.Qt  # type: PySide2.QtCore.Qt

QColor = QtGui.QColor  # type: PySide2.QtGui.QColor
QGuiApplication = QtGui.QGuiApplication  # type: PySide2.QtGui.QGuiApplication
QQuickView = QtQuick.QQuickView  # type: PySide2.QtQuick.QQuickView

QJSValue = QtQml.QJSValue  # type: PySide2.QtQml.QJSValue

if PYSIDE2:
    Property = QtCore.Property
    Slot = QtCore.Slot
    Signal = QtCore.Signal

elif PYQT5:
    Property = QtCore.pyqtProperty
    Slot = QtCore.pyqtSlot
    Signal = QtCore.pyqtSignal
