# Copyright 2016 Philipp Braeuer
# This file is part of CloneApp.
#
# CloneApp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CloneApp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CloneApp. If not, see <http://www.gnu.org/licenses/>.

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
