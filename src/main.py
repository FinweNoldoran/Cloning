from PyQt5 import QtWidgets, QtCore
import sys
import design
import pydna
import Bio.Restriction as br
import matplotlib
matplotlib.use('Qt5Agg')
import pydna
from pydna.gel import weight_standard_sample
from gelwindow import myplots

'''
CloneApp main python file. All windows are defined here, currently there is no help or update window. These are on my to do.
'''

class CloneApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CloneApp, self).__init__(parent)
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
        self.digest_vec.clicked.connect(self.open_plot)
        self.actionHelp_Menu.triggered.connect(self.help_menu)

    def help_menu(self):
        try:
            import webbrowser
            webbrowser.open('https://github.com/FinweNoldoran/Cloning')
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText("Cound not open help.")
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setStandardButtons(QtWidgets.QMessageBox.Close)
            msg.exec_()

        # the clone button, maybe only enable when all inputs are there?
    def open_plot(self):
        plotwindow = myplots(self, parent=self)
        plotwindow.show()

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
            if not hasattr(self, 'tarseq'):
                try:
                    if self.cir_tar.isChecked():
                        self.tarseq = pydna.parse(str(self.target.text()))[0].looped()
                    else:
                        self.tarseq = pydna.parse(str(self.target.text()))[0]
                except TypeError:
                    self.textBrowser.append("Could not read input files")
            if hasattr(self, 'tarseq'):
                ana = br.Analysis(br.RestrictionBatch(br.CommOnly), self.tarseq.seq)
                options = br.RestrictionBatch(ana.with_sites())
                enz = options.as_string()
            else:
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
        if not hasattr(self, 'tarseq'):
            try:
                if self.cir_tar.isChecked():
                    self.tarseq = pydna.parse(str(self.target.text()))[0].looped()
                else:
                    self.tarseq = pydna.parse(str(self.target.text()))[0]
            except TypeError:
                # print that you cant parse file with a proper dialogue
                #self.inputs.clear()
                #self.target.clear()
                self.textBrowser.append("Could not read input files")
        try:
            if not self.checkBox.isChecked():
                self.enzyme3 = br.RestrictionBatch([str(self.enzyC.currentText())]).get(str(self.enzyC.currentText()))
                self.enzyme4 = br.RestrictionBatch([str(self.enzyD.currentText())]).get(str(self.enzyD.currentText()))
            self.enzyme1 = br.RestrictionBatch([str(self.enzyA.currentText())]).get(str(self.enzyA.currentText()))
            self.enzyme2 = br.RestrictionBatch([str(self.enzyB.currentText())]).get(str(self.enzyB.currentText()))
        except (ValueError, TypeError):
            self.textBrowser.append("No enzyme selection")
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
        '''This function does some input checking, after the previous functions have parsed most of the inputs.
        The target sequence is parsed again as in the populate_frag function. A PCR reaction is run.
        Sequences are digested and ligated, and the output is saved to self.result Which is always assumed to be a looped stucture.
        '''
        try:
            if self.cir_in.isChecked():
                self.inseq = pydna.parse(str(self.inputs.text()))[0].looped()
            else:
                self.inseq = pydna.parse(str(self.inputs.text()))[0]
            if self.cir_tar.isChecked():
                self.tarseq = pydna.parse(str(self.target.text()))[0].looped()
            else:
                self.tarseq = pydna.parse(str(self.target.text()))[0]
        except TypeError:
            # print that you cant parse file with a proper dialogue
            self.textBrowser.append("Could not read input files")
        except IndexError:
            self.textBrowser.append("Are you sure you have input files?")
        try:
            self.pcr_product = pydna.pcr(self.fw_primer, self.rv_primer, self.inseq)
            self.textBrowser.append(str(self.pcr_product.figure()))
            self.textBrowser.append("\n")
            ov1, insert, ov2 = self.pcr_product.cut(self.enzyme1, self.enzyme2)
            # need to allow different enzymes here!
            if not self.checkBox.isChecked():
                target_cut = self.tarseq.cut(self.enzyme3, self.enzyme4)
            else:
                target_cut = self.tarseq.cut(self.enzyme1, self.enzyme2)
            target_index = self.frag_list.currentIndex()
            target = target_cut[target_index]
            # print target
            self.result = (target + insert).looped()
            self.textBrowser.append("Success! Your vector is %d base pairs long. \n" % len(self.result.seq))
        except UnboundLocalError:
            self.textBrowser.append("Fill out all inputs")
        except:
            self.textBrowser.clear()
            self.textBrowser.append("Something went wrong, perhaps the fragments do not fit together?\n")
            try:
                try:
                    self.textBrowser.append("Input sequence with ROI ends look like: \n")
                    self.textBrowser.append(str(insert.seq.fig()))
                except:
                    self.textBrowser.append("There appears to be an issue with the sequence containing your gene of interest.")
                try:
                    self.textBrowser.append("\nTarget Vecotor ends look like:\n")
                    self.textBrowser.append(str(target.seq.fig()))
                except:
                    self.textBrowser.append("There appears to be an issue with your target vector sequence.")
            except:
                return
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
    form = CloneApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
