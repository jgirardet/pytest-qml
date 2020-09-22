from pytestqml.qt import QObject, Signal, Property


class Bla(QObject):
    rienChanged = Signal()

    @Property(str, notify=rienChanged)
    def rien(self):
        return "rien"
