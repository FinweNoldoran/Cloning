# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gel.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

class Ui_Dialog(object):
    def setupUi(self, Dialog, mainwindow):
        Dialog.setObjectName("Dialog")
        Dialog.resize(633, 414)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        # self.gel = plotter(Dialog, width=5, height=4, dpi=100, mainwindow=mainwindow)
        self.figure = plt.figure()
        self.gel = FigureCanvas(self.figure)
        self.gel.setMinimumSize(QtCore.QSize(320, 0))
        self.gel.setObjectName("gel")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.gel)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout.addWidget(self.gel)
        self.navbar = NavigationToolbar(self.gel, Dialog)
        self.navbar.setObjectName("navbar")
        self.verticalLayout.addWidget(self.navbar)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.seq_sele = QtWidgets.QComboBox(self.groupBox_2)
        self.seq_sele.setObjectName("seq_sele")
        self.verticalLayout_2.addWidget(self.seq_sele)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setEnabled(True)
        self.groupBox.setCheckable(False)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.select_enz1 = QtWidgets.QComboBox(self.groupBox)
        self.select_enz1.setEnabled(False)
        self.select_enz1.setCurrentText("")
        self.select_enz1.setObjectName("select_enz1")
        self.horizontalLayout_4.addWidget(self.select_enz1)
        self.check_enzy1 = QtWidgets.QCheckBox(self.groupBox)
        self.check_enzy1.setText("")
        self.check_enzy1.setObjectName("check_enzy1")
        self.horizontalLayout_4.addWidget(self.check_enzy1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.select_enz2 = QtWidgets.QComboBox(self.groupBox)
        self.select_enz2.setEnabled(False)
        self.select_enz2.setCurrentText("")
        self.select_enz2.setObjectName("select_enz2")
        self.horizontalLayout_5.addWidget(self.select_enz2)
        self.check_enzy2 = QtWidgets.QCheckBox(self.groupBox)
        self.check_enzy2.setText("")
        self.check_enzy2.setObjectName("check_enzy2")
        self.horizontalLayout_5.addWidget(self.check_enzy2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.plot_update = QtWidgets.QPushButton(Dialog)
        self.plot_update.setObjectName("plot_update")
        self.verticalLayout_3.addWidget(self.plot_update)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.close_plot = QtWidgets.QPushButton(Dialog)
        self.close_plot.setObjectName("close_plot")
        self.verticalLayout_3.addWidget(self.close_plot)
        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox_2.setTitle(_translate("Dialog", "Sequence Selection"))
        self.groupBox.setTitle(_translate("Dialog", "Enzyme Selction"))
        self.plot_update.setText(_translate("Dialog", "Update Plot"))
        self.close_plot.setText(_translate("Dialog", "Quit"))
        

