def pytest_qml_select_files(path, parent):
    """Here we put qml configure options"""


def pytest_qml_context_properties() -> dict:
    """returns a {key:value} dict with :
    key: str  variable name in context
    value: QObject instance of object
    """


def pytest_qmlEngineAvailable(engine):
    """Called when the QML engine is available. Any import paths, plugin paths, and extra
    file selectors will have been set on the engine by this point. This function is called
    once for each QML test file, so any arguments are unique to that test. For example, this
    means that each QML test file will have its own QML engine."""
