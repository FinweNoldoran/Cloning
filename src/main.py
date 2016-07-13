from PyQt5 import QtWidgets
import sys
import design
import os


# Notes:

# Figure out the vertical and horizontal layout stuff for qt design
# use lineEdit for holding file location

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.br_in.clicked.connect(lambda: self.browse_folder(self.inputs))
        self.br_tar.clicked.connect(lambda: self.browse_folder(self.target))
        #self.cir_in if checked
        #self.cir_tar if checked
        #self.enzyA and B only enable after primers are there, and genereate slectoin frome enzymes possible in those
        

    def browse_folder(self, line):
        line.clear()
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Pick a file")[0]
        line.setText(file_name)
       

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
