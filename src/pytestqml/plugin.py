from pathlib import Path
from time import sleep
from typing import List, Tuple

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from pytestqml.exceptions import PytestQmlError
from pytestqml.qmlbot import QmlBot

import pytest
from pytestqml.qt import QGuiApplication, Slot, QtCore, QQuickView, QtTest, QPoint
from pytestqt.wait_signal import MultiSignalBlocker, SignalBlocker


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
        )  # context_properties=context_properties)


def collect_one_tst_file(path, parent):  # , context_properties={}):
    return QMLFile.from_parent(parent, fspath=path)


class QMLFile(pytest.File):
    def __init__(self, fspath, parent):  # , context_properties={}):
        super().__init__(fspath, parent)  # , config, session, nodeid)
        # self.context_properties = context_properties

    def collect(self):
        if self.config.getoption("skip-qml"):
            return []
        self._setup_view()  # app should exists has long has collect()

        # add tst_file.qml to the view, fail test if errors
        self.view.setSource(QtCore.QUrl.fromLocalFile(self.name))
        if self.view.status() != QQuickView.Ready:
            pytest.fail("\n".join((err.toString() for err in self.view.errors())))

        # iter over all children of tst_file.qml root.
        # TestCases are selected if they a name starting with "Test"
        for testcase in self.view.rootObject().children():
            testCaseName = testcase.property("name")
            if testCaseName and testCaseName.startswith("Test"):
                testcase.name = testCaseName
                collected_js = testcase.property("collected")
                if collected_js:
                    collected = collected_js.toVariant()
                    for testname in collected:
                        yield QMLItem.from_parent(
                            self, name=testname, testcase=testcase
                        )

        # del view # delete view before app

    def _set_context_properties(self, view: QQuickView):
        for k, v in self.context_properties.items():
            view.rootContext().setContextProperty(k, v)

    def _setup_view(self) -> Tuple[QGuiApplication, QQuickView]:
        self.app = QGuiApplication.instance() or QGuiApplication([])
        self.view = QQuickView()  # doit exister apres collect()
        engine = self.view.engine()
        engine.setImportPathList([str(Path(__file__).parent)] + engine.importPathList())
        self.qmlbot = QmlBot(self.view, settings={"whenTimeout":2000})
        self.view.rootContext().setContextProperty("qmlbot", self.qmlbot)
        # self.view.setFramePosition(QPoint(50, 50));
        # if self.view.size().isEmpty():# { // Avoid hangs with empty windows.
        #     self.view.resize(200, 200)
        self.view.exposeEvent = lambda ev: self.qmlbot.windowShownChanged.emit()
        # self._set_context_properties(self.view)
        return self.view


class QMLItem(pytest.Item):
    def __init__(self, name, parent, testcase):
        super().__init__(testcase.name + "::" + name, parent)
        self.testname = name
        self.testcase = testcase

    def runtest(self):
        view = self.parent.view
        qmlbot = self.parent.qmlbot

        with qmlbot.wait_signal(
                self.testcase.testCompleted, timeout=10000, raising=True,
        ) as block:
            self.testcase.setProperty("testToRun", self.testname)
            view.show()
        res = self.testcase.property("result").toVariant()
        print(res)
        view.hide()
        del view
        del self.parent.view
        self._handle_result(res)

    def repr_failure(self, excinfo):
        print(excinfo)
        return excinfo.value

    def reportinfo(self):
        return self.fspath, 0, f"{self.parent.name}: {self.name}"

    def _handle_result(self, result:dict):
        if not result:
            return
        elif "type" in result:
            if result["type"] == "SkipError":
                print(f'Skipped: {result["message"]}') # either message is not printed
                pytest.skip(msg=result["message"])


        raise PytestQmlError("\n".join((result["type"], result["message"], result["stack"])))


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
