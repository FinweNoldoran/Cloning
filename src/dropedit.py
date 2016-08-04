from PyQt5 import QtWidgets, QtCore


class dropedit(QtWidgets.QLineEdit):   # subclass
    def __init__(self, parent=None):
        super(dropedit, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():   # if file or link is dropped
            url = QtCore.QUrl(event.mimeData().urls()[0])   # get first url
            self.setText(url.path())   # assign first url to editline
