from PyQt5 import QtWidgets, QtCore
import sys
import design
import geldesign
import pydna
import Bio.Restriction as br
import matplotlib
matplotlib.use('Qt5Agg')
import pydna
from pydna.gel import weight_standard_sample


# Notes:

# Figure out the vertical and horizontal layout stuff for qt design
# use lineEdit for holding file location

class myplots(QtWidgets.QDialog, geldesign.Ui_Dialog):
    def __init__(self, mainwindow, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self, mainwindow=mainwindow)
        self.main_window = mainwindow
        self.close_plot.clicked.connect(self.close)  # works
        self.plot_update.clicked.connect(self.update_plot)
        self.check_enzy1.stateChanged.connect(lambda: self.update_enz(self.check_enzy1, self.select_enz1))
        self.check_enzy2.stateChanged.connect(lambda: self.update_enz(self.check_enzy2, self.select_enz2))
        self.seq_sele.addItems(['1. Sequence with ROI', '2. Target Vector', '3. PCR Product', '4. Resultant Vector'])
        self.enzy_list = br.CommOnly.as_string()
        self.enzy_list.sort()
        self.select_enz1.addItems(self.enzy_list)
        self.select_enz2.addItems(self.enzy_list)

    def update_enz(self, enz_check, enz_select):
        if enz_check.isChecked():
            enz_select.setEnabled(True)
        else:
            enz_select.setEnabled(False)
        return

    def update_plot(self):
        try:
            if self.seq_sele.currentIndex() == 0:  # input sequence
                try:
                    gene = self.main_window.inseq
                except AttributeError:
                    try:
                        if self.main_window.cir_tar.isChecked():
                            gene = pydna.parse(str(self.main_window.inputs.text()))[0].looped()
                        else:
                            gene = pydna.parse(str(self.main_window.inputs.text()))[0]
                    except TypeError:
                        self.main_window.textBrowser.append("Could not read input files")
            elif self.seq_sele.currentIndex() == 1:  # target sequence
                try:
                    gene = self.main_window.tarseq
                except AttributeError:
                    try:
                        if self.main_window.cir_tar.isChecked():
                            gene = pydna.parse(str(self.main_window.target.text()))[0].looped()
                        else:
                            gene = pydna.parse(str(self.main_window.target.text()))[0]
                    except TypeError:
                        self.main_window.textBrowser.append("Could not read input files")
            elif self.seq_sele.currentIndex() == 2:  # pcr product
                try:
                    gene = self.main_window.pcr_product
                except AttributeError:
                    self.main_window.textBrowser.append("You need to run the PCR first.")
                    self.close()
                    return
            elif self.seq_sele.current() == 3:
                try:
                    gene = self.main_window.result
                except AttributeError:
                    self.main_window.textBrowser.append("You have to clone it first!")
                    self.close()
                    return
            else:
                return
        except Exception, e:
            self.main_window.textBrowser.append("DNA selection error " + str(e))
        try:
            if self.check_enzy1.isChecked() and not self.check_enzy2.isChecked():
                self.update_figure(gene, enz1=str(self.select_enz1.currentText()), enz2=None)
            elif self.check_enzy2.isChecked() and not self.check_enzy1.isChecked():
                self.update_figure(gene, enz1=None, enz2=str(self.select_enz2.currentText()))
            elif self.check_enzy1.isChecked() and self.check_enzy2.isChecked():
                self.update_figure(gene, enz1=str(self.select_enz1.currentText()), enz2=str(self.select_enz2.currentText()))
            elif not self.check_enzy1.isChecked() and not self.check_enzy2.isChecked():
                self.update_figure(gene, enz1=None, enz2=None)
            else:
                self.main_window.textBrowser.append("Enzyme selection error")
        except Exception, e:
            print "enzyme selector error " + str(e)
            return
        try:
            # self.figure.draw()  # this executes!
            self.gel.draw()  # so does this!
        except Exception, e:
            print "gel draw error " + str(e)
            return

    def update_figure(self, gene, enz1=None, enz2=None):
        st = weight_standard_sample('1kb_GeneRuler')
        # enz1 and 2 type error?
        # no enzyme
        try:
            # self.clear() plotter has not attribute clear
            # self.fig.clear()
            # del(self.fig) enzyme selector error 'myplots' object has no attribute 'gel'
            if enz1 is None and enz2 is None:
                pydna.Gel([st, [gene]]).run(infig=self.figure)  # check if gnee needs to be in list -- it does this command works
                return
            # single enzyme
            elif (enz1 is not None and enz2 is None):
                enzyme = br.RestrictionBatch([enz1]).get(enz1)
                cuts = gene.cut(enzyme)
                pydna.Gel([st, cuts]).run(infig=self.figure)
                return
            elif (enz1 is None and enz2 is not None):
                enzyme = br.RestrictionBatch([enz2]).get(enz2)
                cuts = gene.cut(enzyme)
                pydna.Gel([st, cuts]).run(infig=self.figure)
                return
            # both enzymes
            elif (enz1 is not None and enz2 is not None):
                ezA = br.RestrictionBatch([enz1]).get(enz1)
                ezB = br.RestrictionBatch([enz2]).get(enz2)
                cuts = gene.cut(ezA, ezB)
                pydna.Gel([st, cuts]).run(infig=self.figure)
                return
            else:
                self.mainwindow.textBrowser.append("could not update figure")
        except Exception, e:
            print "plotter error: " + str(e)


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