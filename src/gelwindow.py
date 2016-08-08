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

from PyQt5 import QtWidgets
import geldesign
import pydna
import Bio.Restriction as br
import matplotlib
matplotlib.use('Qt5Agg')
import pydna
from pydna.gel import weight_standard_sample


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
        self.check_enzy1.setToolTip("Choose an enzyme to digest your sequence.")
        self.check_enzy2.stateChanged.connect(lambda: self.update_enz(self.check_enzy2, self.select_enz2))
        self.check_enzy2.setToolTip("Choose a second enzyme to digest your sequence.")
        self.seq_sele.addItems(['1. Sequence with ROI', '2. Target Vector', '3. PCR Product', '4. Resultant Vector'])
        self.seq_sele.setToolTip("Select a sequence to run on your gel.")
        self.enzy_list = br.CommOnly.as_string()
        self.enzy_list.sort()
        self.select_enz1.addItems(self.enzy_list)
        self.select_enz2.addItems(self.enzy_list)
        self.ladder.addItems(['1kb GeneRuler', '1kb+ GeneRuler', 'Mix GeneRuler', 'High Range GeneRuler'])
        self.ladder.setToolTip("Choose a DNA ladder.")

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
        except IndexError:
            self.main_window.textBrowser.append("The selected sequence is not available.")
            return
        except Exception, e:
            self.main_window.textBrowser.append("DNA selection error " + str(e))
            return
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
            self.main_window.textBrowser.append("Enzyme selector error " + str(e))
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
        def print_fragments(frags):
            out = "\nFragment lengths (bp): \n"
            for i, f in enumerate(frags):
                out += '%i. %i\n' % (i+1, len(f.seq))
            self.gel_browser.append(out)
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
        try:
            if enz1 is None and enz2 is None:
                pydna.Gel([st, [gene]]).run(infig=self.figure)  # check if gnee needs to be in list -- it does this command works
                return
            # single enzyme
            elif (enz1 is not None and enz2 is None):
                enzyme = br.RestrictionBatch([enz1]).get(enz1)
                cuts = gene.cut(enzyme)
                pydna.Gel([st, cuts]).run(infig=self.figure)
                print_fragments(cuts)
                return
            elif (enz1 is None and enz2 is not None):
                enzyme = br.RestrictionBatch([enz2]).get(enz2)
                cuts = gene.cut(enzyme)
                pydna.Gel([st, cuts]).run(infig=self.figure)
                print_fragments(cuts)
                return
            # both enzymes
            elif (enz1 is not None and enz2 is not None):
                ezA = br.RestrictionBatch([enz1]).get(enz1)
                ezB = br.RestrictionBatch([enz2]).get(enz2)
                cuts = gene.cut(ezA, ezB)
                # print cuts
                pydna.Gel([st, cuts]).run(infig=self.figure)
                print_fragments(cuts)
                return
            else:
                self.mainwindow.textBrowser.append("could not update figure")
        except Exception, e:
            print "plotter error: " + str(e)
