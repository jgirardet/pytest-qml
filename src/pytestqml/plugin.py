from pytestqml.nodes import QMLFile
import pytest


def pytest_addhooks(pluginmanager):
    """ import  and regiter hooks"""
    from pytestqml import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_collect_file(path, parent):
    res = parent.config.pluginmanager.hook.pytest_qml_select_files(
        path=path, parent=parent
    )
    if res:
        return res[0]


def pytest_qml_select_files(path, parent):
    return collect_any_tst_files(path, parent)


def pytest_configure(config):
    config.addinivalue_line("markers", "qmltest: mark a item as qml")
    config.addinivalue_line("markers", "qmlfile: mark a item as qml testfile")


def collect_any_tst_files(path, parent):
    if path.ext == ".qml" and path.basename.startswith("tst_"):
        return collect_one_tst_file(
            path,
            parent,
        )


def collect_one_tst_file(path, parent):

    return QMLFile.from_parent(parent, fspath=path)


def pytest_addoption(parser):
    group = parser.getgroup("qml")
    group.addoption(
        "--skip-qml",
        dest="skip-qml",
        action="store_true",
        default=False,
        help="slip all qml tests",
    )
    # group.addoption(
    #     '--foo',
    #     action='store',
    #     dest='dest_foo',
    #     default='2020',
    #     help='Set the value for the fixture "bar".'
    # )

    parser.addini("HELLO", "Dummy pytest.ini setting")


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo
