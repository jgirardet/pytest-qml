from pathlib import Path


import sys

from pytestqml.qt import QObject, Slot, qmlRegisterType

sys.path.append(str(Path(__file__).parents[1]))
from module import Bla


qmlRegisterType(Bla, "MyNewType", 1, 0, "Bla")
# def pytest_configure():
#     pass


#
# def pytest_qml_applicationAvailable():
#     qmlRegisterType(Bla, "MyNewType", 1, 0, "Bla")


class CustomProp(QObject):
    @Slot(result=str)
    def customSlot(self):
        return "customSlot"


def pytest_qml_context_properties():
    return {"cp": CustomProp()}


aa = CustomProp()

# from PySide2.QtCore import
def pytest_qml_qmlEngineAvailable(engine):
    #     print(engine.rootContext())
    # vv = {"a": CustomProp()}
    engine.aa = CustomProp()
    engine.rootContext().setContextProperty("a", engine.aa)


# engine.rootContext().setContextProperty("cp", a)
# engine.addImportPath("/tmp")
# engine.rootContext().setContextProperty("cp", CustomProp())
# print(engine.rootContext().contextProperty("cp"))
