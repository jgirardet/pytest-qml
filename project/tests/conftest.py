from pathlib import Path

from PySide2.QtCore import QObject, Slot
from PySide2.QtQml import qmlRegisterType
import sys
sys.path.append(str(Path(__file__).parents[1]))
from module import Bla

def pytest_configure():
    qmlRegisterType(Bla, "MyNewType", 1, 0, "Bla")


class CustomProp(QObject):
    @Slot(result=str)
    def customSlot(self):
        return "customSlot"

def pytest_qml_context_properties():
    return {
        "cp":CustomProp()
    }