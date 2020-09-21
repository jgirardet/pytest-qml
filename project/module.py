from PySide2.QtCore import QObject, Property, Signal


class Bla(QObject):
    rienChanged = Signal()

    @Property(str, notify=rienChanged)
    def rien(self):
        return "rien"
