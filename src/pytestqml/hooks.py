from pytestqml.qt import QQmlEngine


def pytest_qml_select_files(path, parent):
    """Here we put qml configure options"""


def pytest_qml_context_properties() -> dict:
    """returns a {key:value} dict with :
    key: str  variable name in context
    value: QObject instance of object
    """


def pytest_qml_qmlEngineAvailable(engine: QQmlEngine):
    """Called when the QML engine is available. Any import paths, plugin paths, and extra
    file selectors will have been set on the engine by this point. This function is called
    once for each QML test file, so any arguments are unique to that test. For example, this
    means that each QML test file will have its own QML engine."""


def pytest_qml_applicationAvailable(app):
    """Called right after the QApplication object was instantiated. Use this function
    to perform setup that does not require a QQmlEngine instance. "app" parameter wich is
    absent from C++ implementation of "applicationAvailable" is added here for convenience"""
