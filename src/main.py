from PyQt5 import QtWidgets, QtCore
import sys
import design
import pydna
import Bio.Restriction as br


# Notes:

# Figure out the vertical and horizontal layout stuff for qt design
# use lineEdit for holding file location


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("CloneApp")
        self.br_in.clicked.connect(lambda: self.browse_folder(self.inputs))
        self.br_tar.clicked.connect(lambda: self.browse_folder(self.target))
        self.run.clicked.connect(self.clone)
        self.pr_fw.textEdited.connect(lambda: self.fwprimer_done(self.pr_fw))
        self.pr_rv.textEdited.connect(lambda: self.rvprimer_done(self.pr_rv))
        self.valid = "natgc"
        self.fw_primer = ""
        self.rv_primer = ""
        self.checkBox.stateChanged.connect(self.target_enzymes)
        self.frag_list.popupAboutToBeShown.connect(self.populate_frag)
        self.save_vec.clicked.connect(self.save_result)

        # the clone button, maybe only enable when all inputs are there?

    def browse_folder(self, line):
        line.clear()
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Pick a file", "/",)[0]
        line.setText(file_name)
        # self.textBrowser.append("Testing")

    def fwprimer_done(self, primer):
        temp = primer.text().lower()
        if all(i in self.valid for i in temp):
            self.pr_fw.setStyleSheet("")
            temp = ">fw_primer\n" + temp
            try:
                self.fw_primer = pydna.read(temp, ds=False)
                ana = br.Analysis(br.RestrictionBatch(br.CommOnly), self.fw_primer.seq)
                options = br.RestrictionBatch(ana.with_sites())
                options = options.as_string()
                options.sort()
                self.enzyA.clear()
                self.enzyA.addItems(options)
            except (AttributeError, TypeError, ValueError):
                # ask for proper input
                self.textBrowser.append("error")
                return
        else:
            self.pr_fw.setStyleSheet("border: 1px solid red;")
            return

    def rvprimer_done(self, primer):
        temp = primer.text().lower()
        if all(i in self.valid for i in temp):
            self.pr_rv.setStyleSheet("")
            temp = ">rv_primer\n" + temp
            try:
                self.rv_primer = pydna.read(temp, ds=False)
                ana = br.Analysis(br.RestrictionBatch(br.CommOnly), self.rv_primer.seq)
                options = br.RestrictionBatch(ana.with_sites())
                options = options.as_string()
                options.sort()
                self.enzyB.clear()
                self.enzyB.addItems(options)  # test sort
            except (AttributeError, TypeError, ValueError):
                return
        else:
            self.pr_rv.setStyleSheet("border: 1px solid red;")
            return

    def target_enzymes(self):
        if not self.checkBox.isChecked():
            enz = br.CommOnly.as_string()
            enz.sort()
            self.enzyC.setEnabled(True)
            self.enzyC.addItems(enz)
            self.enzyD.setEnabled(True)
            self.enzyD.addItems(enz)
        else:
            self.enzyC.setEnabled(False)
            self.enzyD.setEnabled(False)

    def populate_frag(self):
        #  self.frag_list.addItem("Test")
        try:
            if self.cir_tar.isChecked():
                tarseq = pydna.parse(str(self.target.text()))[0].looped()
            else:
                tarseq = pydna.parse(str(self.target.text()))[0]
        except TypeError:
            # print that you cant parse file with a proper dialogue
            #self.inputs.clear()
            #self.target.clear()
            self.textBrowser.append("Could not read input files")
        try:
            # This fails
            if not self.checkBox.isChecked():
                self.enzyme3 = br.RestrictionBatch([str(self.enzyC.currentText())]).get(str(self.enzyC.currentText()))
                self.enzyme4 = br.RestrictionBatch([str(self.enzyD.currentText())]).get(str(self.enzyD.currentText()))
            self.enzyme1 = br.RestrictionBatch([str(self.enzyA.currentText())]).get(str(self.enzyA.currentText()))
            self.enzyme2 = br.RestrictionBatch([str(self.enzyB.currentText())]).get(str(self.enzyB.currentText()))
        except (ValueError, TypeError):
            self.textBrowser.append("No enzyme selection")
            # print self.enzyA.currentText()  # this is empty
            # print self.enzyA.currentIndex()
            # self.textBrowser.append(self.enzyA.currentData())
        try:
            self.frag_list.clear()
            if not self.checkBox.isChecked():
                target_cut = tarseq.cut(self.enzyme3, self.enzyme4)
            else:
                target_cut = tarseq.cut(self.enzyme1, self.enzyme2)
            for i, fragment in enumerate(target_cut):
                self.frag_list.addItem('Fragment %d, with %d basepairs ' % (i+1, len(fragment.seq)))
        except:
            return  # better errors here
        return

    def clone(self):
        # This is the meat and potatoes
        try:
            if self.cir_in.isChecked():
                inseq = pydna.parse(str(self.inputs.text()))[0].looped()
            else:
                inseq = pydna.parse(str(self.inputs.text()))[0]
            if self.cir_tar.isChecked():
                tarseq = pydna.parse(str(self.target.text()))[0].looped()
            else:
                tarseq = pydna.parse(str(self.target.text()))[0]
        except TypeError:
            # print that you cant parse file with a proper dialogue
            self.textBrowser.append("Could not read input files")
        except IndexError:
            self.textBrowser.append("Are you sure you have input files?")
        try:
            pcr_product = pydna.pcr(self.fw_primer, self.rv_primer, inseq)
            self.textBrowser.append(str(pcr_product.figure()))
            self.textBrowser.append("\n")
            ov1, insert, ov2 = pcr_product.cut(self.enzyme1, self.enzyme2)
            # need to allow different enzymes here!
            if not self.checkBox.isChecked():
                target_cut = tarseq.cut(self.enzyme3, self.enzyme4)
            else:
                target_cut = tarseq.cut(self.enzyme1, self.enzyme2)
            target_index = self.frag_list.currentIndex()
            target = target_cut[target_index]
            print target
            self.result = (target + insert).looped()
            self.textBrowser.append("Success! Your vector is %d base pairs long. \n" % len(self.result.seq))
        except UnboundLocalError:
            self.textBrowser.append("Fill out all inputs")
        except:
            self.textBrowser.append("Something went wrong, perhaps the fragments do not fit together?\n")
            try:
                self.textBrowser.append("Input sequence with ROI ends: \n")
                self.textBrowser.append(str(insert.seq.fig()))
                self.textBrowser.append("\nTarget Vecotor ends are:\n")
                self.textBrowser.append(str(target.seq.fig()))
        return

    def save_result(self):
        try:
            fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File Name', '/')[0]
            if fileName:
                self.result.write(fileName)
                self.textBrowser.append("Saved file %s" % fileName)
        except:
            self.textBrowser.append("Something went wrong while trying to save your file.")
        return


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
