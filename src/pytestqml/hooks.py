def pytest_qml_select_files(path, parent):
    """Here we put qml configure options"""


def pytest_qml_context_properties() -> dict:
    """returns a {key:value} dict with :
    key: str  variable name in context
    value: QObject instance of object
    """
