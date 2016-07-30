# CloneApp

## Introduction
CloneApp is a simple GUI wrapper for the python pydna library, currently it supports a standard restriction cloning work flow. It also provides an interface to simulate a gel of your sequences, so you can see what an analytical digest should look like and where your PCR product should run.


## Basic Use

### What you need
For a basic run cloning simulation, you will require four pieces of information:

1. A sequence file (pydna compatible: .gb, .fasta, .embl) containing the gene you wish to clone, referred to from here on as your roi.
2. A sequence file containing the vector you wish to clone into.
3. A forward primer sequence.
4. A reverse primer sequence.


### Lets Go!

Browse for your roi and target vector sequences in their respective boxes. If the sequence files represent looped plasmids, keep the circular check box checked, otherwise uncheck this. The circular check box will force your sequence to be understood as a complete plasmid.

Enter in your plasmid sequences, on the right a list of restriction enzymes with sites in your primers will appear. Please select the ones you wish to use. 

Target fragment selection; either keep the same enzymes you are using to cut your roi PCR product or select new ones. This will generate a list of DNA fragments of your target vector. Generally there should be two, and you will be using the larger, which should appear first in the list. 

Alright, now press the button that says PCR, ligate and clone.

You will see some output in the textbox below, including the melting temperatures of your PCR primers and if any errors were encountered. Currently the error reporting will be rather mysterious.

You can save the result, any annotated features should be saved from your input sequences. You can check the sequence out in your favourite viewer.

### Run a Gel

If you click the Analytical Digest button on the bottom left, a new window will appear. Here you can choose a sequence (roi input, target vector, PCR, and resulting vector). You can run these on a gel, with your choice of 0, 1 or 2 enzyme digestion. Please take the gel simulation results with a pinch of salt (For example, currently an undigested plasmid will run a the same place as an equivalent length of linear DNA. You can obviously forget about any supercoiling effects here too.). 


## Run Your Own

Currently there is only a OS X distribution, and I am not sure how to distribute binaries to other systems as I do not have access to them and the available wrappers struggle with a matplotlib pyqt5 python application. Suggestions welcome. Currently I am using PyInstaller.

You can however run the source, I advise running in a virtual environment, as there are currently several quirks of pydna (e.g. Pint must be version 0.6) and I have edited a file in the pydna library. There is an upcoming pydna release in python3 so things may change. Currently things are running in python 2.7.12 and the dependencies for this project can be found in the freeze file. In addition you will need to install pyqt5 and sip. I find the easiest way to get these working in a virtualenv, is to install them system wide (e.g. via homebrew) and then copy the files in your python lib to the virtual env ```virutalenv/lib/python2.7/``` folder. I will provided a modified gel.py from pydna in the ```modified pydna``` directory, which you will have to use and replace the one installed in your ```virtualenv/lib/python2.7/site-packages/pydna``` folder.

