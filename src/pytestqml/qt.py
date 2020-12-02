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

QtCore = None
QtGui = None
QtQuick = None
QtTest = None
QtQml = None


COMMON = ["QtCore", "QtGui", "QtQuick", "QtTest", "QtQml"]
for module in COMMON:
    key = module.split(".")[-1]
    vars()[module] = import_module(".".join((qtapi, module)))

# QtCore
QDateTime = QtCore.QDateTime
QEventLoop = QtCore.QEventLoop
QObject = QtCore.QObject
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
Qt = QtCore.Qt
QUrl = QtCore.QUrl

# QtGui
QColor = QtGui.QColor
QGuiApplication = QtGui.QGuiApplication
QKeySequence = QtGui.QKeySequence
QVector3D = QtGui.QVector3D
QWheelEvent = QtGui.QWheelEvent
QWindow = QtGui.QWindow

# QtQuick
QQuickView = QtQuick.QQuickView

# QtQml
qmlRegisterType = QtQml.qmlRegisterType
QJSValue = QtQml.QJSValue
QQmlEngine = QtQml.QQmlEngine

# QtTest
QTest = QtTest.QTest

if PYSIDE2:
    Property = QtCore.Property
    Slot = QtCore.Slot
    Signal = QtCore.Signal

elif PYQT5:
    Property = QtCore.pyqtProperty
    Slot = QtCore.pyqtSlot
    Signal = QtCore.pyqtSignal
