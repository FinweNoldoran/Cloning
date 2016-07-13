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
        self.pushButton.clicked.connect(lambda: self.browse_folder(self.lineEdit))

    def browse_folder(self, test):
        #print test
        #self.lineEdit.clear()  # In case there are any existing elements in the list
        test.clear()
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Pick a file")[0]
        print file_name
        # execute getExistingDirectory dialog and set the directory variable to be equal
        # to the user selected directory

        # if directory: # if user didn't pick a directory don't continue
        #     for file_name in os.listdir(directory): # for all files, if any, in the directory
        #  self.lineEdit.setText(file_name)  # add file to the listWidget
        test.setText(file_name)
       

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
