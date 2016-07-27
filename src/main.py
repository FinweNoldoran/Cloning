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

'''
CloneApp main python file. All windows are defined here, currently there is no help or update window. These are on my to do.
'''

class myplots(QtWidgets.QDialog, geldesign.Ui_Dialog):
    '''
    The myplots class defines the window displaying the gel simulation. This is calculated inside the pydna.gel module.
    '''
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
        self.ladder.addItems(['1kb GeneRuler', '1kb+ GeneRuler', 'Mix GeneRuler', 'High Range GeneRuler'])

    def update_enz(self, enz_check, enz_select):
        '''
        Check the state of the digestiong checkbox, and enable or diable the enzyme dropdown lists accordingly.
        '''
        if enz_check.isChecked():
            enz_select.setEnabled(True)
        else:
            enz_select.setEnabled(False)
        return

    def update_plot(self):
        '''
        This function checks the states of all the inputs,
        parses the various options and passes them on to an appropirate call of the pydna gel simulation function,
        via the update_figure function.
        It will attempt to throw usefull exceptions if inputs are misdefined or incorrect. This needs more work.
        '''
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
            elif self.seq_sele.currentIndex() == 3:
                try:
                    gene = self.main_window.result
                except AttributeError:
                    self.main_window.textBrowser.append("You have to clone it first!")
                    self.close()
                    return
            else:
                print "plotting if statment fails"
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
        ''' Once the input is checked by update_plot, the values are passed to this function, which actually runs the pydna gel simulation.
        '''
        try:
            self.gel_browser.clear()
            standards_dict = {0: ['1kb_GeneRuler', [10000, 8000, 6000, 5000, 4000, 3500, 3000, 2500, 2000, 1500, 1000, 750, 500, 250]],
                              1: ['1kb+_GeneRuler', [20000, 10000, 7000, 5000, 4000, 3000, 2000, 1500, 1000, 700, 500, 400, 300, 200, 75]],
                              2: ['Mix_GeneRuler', [10000, 8000, 6000, 5000, 4000, 3500, 3000, 2500, 2000, 1500, 1200, 1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]],
                              3: ['High_Range_GeneRuler', [48502, 24508, 20555, 17000, 15258, 13825, 12119, 10171]]}
            index = self.ladder.currentIndex()
            st = weight_standard_sample(standards_dict.get(index)[0])
            out = 'Ladder (bp): \n' + '\n'.join(['%i' % i for i in standards_dict.get(index)[1]])
            self.gel_browser.append(out)
        except:
            st = weight_standard_sample('1kb_GeneRuler')
            out = "Ladder (bp): \n 10000\n8000\n6000\n5000\n4000\n3500\n3000\n2500\n2000\n1500\n1000\n750\n500\n250"
            self.gel_browser.append(out)
        # print enz1
        # print enz2
        try:
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
                print cuts
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
