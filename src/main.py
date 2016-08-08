# Copyright 2016 Philipp Braeuer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets, QtGui
import sys
import design
import pydna
import Bio.Restriction as br
import matplotlib
from gelwindow import myplots
matplotlib.use('Qt5Agg')

CURRENT_VERSION = '0.0.04'

'''
CloneApp main python file. Main window is defined here.
'''


class CloneApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CloneApp, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("CloneApp")
        self.br_in.clicked.connect(lambda: self.browse_folder(self.inputs))
        self.br_in.setToolTip("Browse for sequence file with region of interest.")
        self.cir_in.setToolTip("Check if sequence is a plasmid. Uncheck if sequence is linear.")
        self.br_tar.clicked.connect(lambda: self.browse_folder(self.target))
        self.br_tar.setToolTip("Browse for sequence file with target vector.")
        self.cir_tar.setToolTip("Check if sequence is a plasmid. Uncheck if sequence is linear.")
        self.run.clicked.connect(self.clone)
        self.run.setToolTip("Click to run the simulated PCR, digestion and ligation.")
        self.pr_fw.textEdited.connect(lambda: self.fwprimer_done(self.pr_fw))
        self.enzyA.setToolTip("Select a restriction enzyme to digest your insert with.")
        self.enzyB.setToolTip("Select a restriction enzyme to digest your insert with.")
        self.pr_rv.textEdited.connect(lambda: self.rvprimer_done(self.pr_rv))
        self.valid = "natgc"
        self.fw_primer = ""
        self.rv_primer = ""
        self.checkBox.stateChanged.connect(self.target_enzymes)
        self.checkBox.setToolTip("Select if you wish to digest your target vector with enzymes differing from those you wish to digest your insert with.")
        self.frag_list.popupAboutToBeShown.connect(self.populate_frag)
        self.frag_list.setToolTip("Choose a target fragment to clone into.")
        self.save_vec.clicked.connect(self.save_result)
        self.digest_vec.clicked.connect(self.open_plot)
        self.digest_vec.setToolTip("Click to run an gel of your sequences.")
        self.external.clicked.connect(self.open_external)
        self.external.setToolTip("Click to open cloned sequence in the default sequence viewer installed on your system.")
        self.actionHelp_Menu.triggered.connect(self.help_menu)
        self.actionCheck_for_Updates.triggered.connect(self.check_updates)
        self.textBrowser.setCurrentFont(QtGui.QFont("Courier New"))

    def error_message(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setText(message)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec_()

    def check_updates(self):
        def parse_version(version):
            try:
                score = [1000, 100, 1]
                split = [int(v) for v in version.split(".")]
                return sum([a*b for a, b in zip(split, score)])
            except:
                self.error_message("Could not update.")
                return

        local = parse_version(CURRENT_VERSION)
        try:
            import urllib2
            vfile = urllib2.urlopen('https://raw.githubusercontent.com/FinweNoldoran/Cloning/master/src/VERSION')
            remote = parse_version(vfile.read().strip())
        except:
            self.error_message("Could not connect to the update site!")
            return

        try:
            if local < remote:
                import webbrowser
                webbrowser.open('https://github.com/FinweNoldoran/Cloning/releases/latest')
            else:
                self.error_message("No new updates available.")
        except:
            self.error_message("Could not connect to update download page.")

    def help_menu(self):
        try:
            import webbrowser
            webbrowser.open('https://github.com/FinweNoldoran/Cloning')
        except:
            self.error_message("Could not connect to help pages.")

    def open_plot(self):
        plotwindow = myplots(self, parent=self)
        plotwindow.show()

    def browse_folder(self, line):
        line.clear()
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Pick a file", "/", "Sequence files(*.gb *.fasta *.embl *.genbank *.fas *.fna *.ffn)")[0]
        line.setText(file_name)

    def get_tarseq(self):
        if not hasattr(self, 'tarseq'):
                try:
                    if self.cir_tar.isChecked():
                        self.tarseq = pydna.parse(str(self.target.text()))[0].looped()
                        return True
                    else:
                        self.tarseq = pydna.parse(str(self.target.text()))[0]
                        return True
                except (TypeError, IndexError):
                    self.textBrowser.append("Could not read input files.")
                    return False
        else:
            return True

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
                self.enzyB.addItems(options)
            except (AttributeError, TypeError, ValueError):
                return
        else:
            self.pr_rv.setStyleSheet("border: 1px solid red;")
            return

    def target_enzymes(self):
        if not self.checkBox.isChecked():
            if self.get_tarseq():
                ana = br.Analysis(br.RestrictionBatch(br.CommOnly), self.tarseq.seq)
                options = br.RestrictionBatch(ana.with_N_sites(1))
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
        if not self.get_tarseq():
            return
        try:
            if not self.checkBox.isChecked():
                self.enzyme3 = br.RestrictionBatch([str(self.enzyC.currentText())]).get(str(self.enzyC.currentText()))
                self.enzyme4 = br.RestrictionBatch([str(self.enzyD.currentText())]).get(str(self.enzyD.currentText()))
            else:
                self.enzyme1 = br.RestrictionBatch([str(self.enzyA.currentText())]).get(str(self.enzyA.currentText()))
                self.enzyme2 = br.RestrictionBatch([str(self.enzyB.currentText())]).get(str(self.enzyB.currentText()))
        except (ValueError, TypeError):
            self.textBrowser.append("No enzyme selection")
        try:
            self.frag_list.clear()
            if not self.checkBox.isChecked():
                target_cut = self.tarseq.cut(self.enzyme3, self.enzyme4)
            else:
                target_cut = self.tarseq.cut(self.enzyme1, self.enzyme2)
            for i, fragment in enumerate(target_cut):
                self.frag_list.addItem('Fragment %d, with %d basepairs ' % (i+1, len(fragment.seq)))
            self.frag_list.setCurrentIndex(0)
        except:
            return  # better errors here
        return

    def clone(self):
        '''This function does some input checking, after the previous functions have parsed most of the inputs.
        The target sequence is parsed again as in the populate_frag function. A PCR reaction is run.
        Sequences are digested and ligated, and the output is saved to self.result Which is always assumed to be a looped stucture.
        '''
        self.textBrowser.clear()
        try:
            if self.cir_in.isChecked():
                self.inseq = pydna.parse(str(self.inputs.text()))[0].looped()
            else:
                self.inseq = pydna.parse(str(self.inputs.text()))[0]
            if not self.get_tarseq():
                return
        except TypeError:
            # print that you cant parse file with a proper dialogue
            self.textBrowser.append("Could not read input files")
            return
        except IndexError:
            self.textBrowser.append("Are you sure you have input files?")
            return
        if not hasattr(self, 'enzyme1'):
            try:
                self.enzyme1 = br.RestrictionBatch([str(self.enzyA.currentText())]).get(str(self.enzyA.currentText()))
                self.enzyme2 = br.RestrictionBatch([str(self.enzyB.currentText())]).get(str(self.enzyB.currentText()))
            except:
                self.textBrowser.append("No enzyme selection.")
                return
        try:
            self.pcr_product = pydna.pcr(self.fw_primer, self.rv_primer, self.inseq)
            self.textBrowser.append("Your PCR reaction looks like this: \n")
            self.textBrowser.append(str(self.pcr_product.figure()))
            self.textBrowser.append("\n")
            ov1, self.insert, ov2 = self.pcr_product.cut(self.enzyme1, self.enzyme2)
            if not self.checkBox.isChecked():
                target_cut = self.tarseq.cut(self.enzyme3, self.enzyme4)
            else:
                target_cut = self.tarseq.cut(self.enzyme1, self.enzyme2)
            target_index = self.frag_list.currentIndex()
            self.target = target_cut[target_index]
            # print target with nice overlaps showing
            self.result = (self.target + self.insert).looped()
            self.print_statment()
            self.textBrowser.append("Success! Your vector is %d base pairs long. \n" % len(self.result.seq))
        except UnboundLocalError:
            self.textBrowser.append("Fill out all inputs")
        except AttributeError:
            self.textBrowser.append("Make sure to choose a target fragment to clone into!")
        except Exception, e:
            if (str(e)[0:16] == "No PCR products!"):
                self.textBrowser.append(str(e))
                return
            self.textBrowser.append("Something went wrong, perhaps the fragments do not fit together?")
            self.textBrowser.append("error " + str(e) + "\n")
            try:
                self.textBrowser.append("Attempting to print sequences: \n")
                self.print_statment()
            except:
                self.textBrowser.append("Failed at printing sequences together. Attempting them seperatly.\n")
            try:
                self.textBrowser.append("Input sequence with ROI ends look like: \n")
                self.textBrowser.append(str(self.insert.seq.fig()))
            except:
                self.textBrowser.append("There appears to be an issue with the sequence containing your gene of interest.")
            try:
                self.textBrowser.append("\nTarget Vecotor ends look like:\n")
                self.textBrowser.append(str(self.target.seq.fig()))
            except:
                self.textBrowser.append("There appears to be an issue with your target vector sequence.")
        return

    def print_statment(self):
        '''
        Writes out the top an bottom sequences around the ligation areas and shows if there are any sequence mismatches.
        '''
        topline = ""
        bottomline = ""

        def second_half():
                topline = ""
                bottomline = ""
                if (self.target.seq.five_prime_end()[0] == "5'"):
                        ovr = len(self.target.seq.five_prime_end()[1])
                        topline += str(self.target.seq)[0:10].lower()
                        bottomline += " " * ovr + str(self.target.seq.reverse_complement())[-10:-ovr][::-1].lower()
                elif (self.target.seq.five_prime_end()[0] == "3'"):
                        ovr = len(self.target.seq.five_prime_end()[1])
                        topline += " " * ovr + str(self.target.seq)[ovr:10].lower()
                        bottomline += str(self.target.seq.reverse_complement())[-10:][::-1].lower()
                elif (self.target.seq.five_prime_end()[0] == 'blunt'):
                        topline += " " + str(self.target.seq)[0:10].lower()
                        bottomline += " " + str(self.target.seq.reverse_complement())[-10:][::-1].lower()
                return [topline, bottomline]

        def in_insert():
                topline = ""
                bottomline = ""
                topline += self.insert.seq.fig().split("\n")[1].upper()
                bottomline += self.insert.seq.fig().split("\n")[2].upper()
                return [topline, bottomline]

        def match_line(topline, bottomline):
            matchline = ""
            for n in zip(topline.lower(), bottomline.lower()):
                if (n[0] == 'a' and n[1] == 't'):
                    matchline += "|"
                elif (n[0] == 't' and n[1] == 'a'):
                    matchline += "|"
                elif (n[0] == 'c' and n[1] == 'g'):
                    matchline += "|"
                elif (n[0] == 'g' and n[1] == 'c'):
                    matchline += "|"
                elif(n[0] == '.' and n[1] == '.'):
                    matchline += '|'
                else:
                    matchline += ":"
            return matchline

        if (self.target.seq.three_prime_end()[0] == 'blunt'):
                topline += str(self.target.seq)[0:10].lower()
                bottomline += str(self.target.seq.reverse_complement())[0:10][::-1].lower()
                topline += in_insert()[0]
                bottomline += in_insert()[1]
                topline += second_half()[0]
                bottomline += second_half()[1]

        elif (self.target.seq.three_prime_end()[0] == "5'"):
                ovr = len(self.target.seq.three_prime_end()[1])
                topline += str(self.target.seq)[-10:-ovr].lower() + " " * ovr
                bottomline += str(self.target.seq.reverse_complement())[0:10][::-1].lower()
                topline += in_insert()[0]
                bottomline += in_insert()[1]
                topline += second_half()[0]
                bottomline += second_half()[1]
        elif (self.target.seq.three_prime_end()[0] == "3'"):
                #  untested
                ovr = len(self.target.seq.three_prime_end()[1])
                topline += str(self.target.seq)[0:10].lower()
                bottomline += str(self.target.seq.reverse_complement())[ovr:10][::-1].lower() + " " * ovr
                topline += in_insert()[0]
                bottomline += in_insert()[1]
                topline += second_half()[0]
                bottomline += second_half()[1]
        else:
                return
        heading = " " * 11 + "INSERT"
        self.textBrowser.append(heading)
        self.textBrowser.append(topline)
        self.textBrowser.append(bottomline)
        self.textBrowser.append("\n\nLigated: \n" + heading)
        matchline = match_line(topline.replace(' ', ''), bottomline.replace(' ', ''))
        self.textBrowser.append(topline.replace(' ', ''))
        self.textBrowser.append(matchline)
        self.textBrowser.append(bottomline.replace(' ', '')+"\n")
        if ":" in matchline:
            self.textBrowser.append("There is a squence mismatch in the ligation area!")

    def save_result(self):
        try:
            pathQFileDialog = QtWidgets.QFileDialog(self)
            pathQFileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            pathQFileDialog.setNameFilter('Gene bank(*.gb)')
            pathQFileDialog.setDefaultSuffix('gb')
            if pathQFileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
                self.savefilename = pathQFileDialog.selectedFiles()[0]
                self.result.write(self.savefilename)
                self.textBrowser.append("Saved file %s " % self.savefilename)
        except:
            self.textBrowser.append("Something went wrong while trying to save your file.")
        return

    def open_external(self):
        #  Currently OS X only
        import os
        if hasattr(self, 'savefilename'):
            try:
                os.system("open" + self.savefile)
            except:
                self.error_message("Could not open in external viewer.")
        else:
            # generate a temporary file
            try:
                import tempfile
                temp = tempfile._get_default_tempdir()
                temp += next(tempfile._get_candidate_names()) + ".gb"
                self.result.write(temp)
                os.system("open " + temp)
                os.remove(temp)
            except AttributeError:
                self.textBrowser.append("Could not open external viewer. Have you cloned your vector already?")
            except:
                self.error_message("Could not open in external viewer.")
        return


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = CloneApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
