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


class ComboBox(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()
