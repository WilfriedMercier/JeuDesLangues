# Mercier Wilfried - IRAP

import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import os
import os.path         as     opath

from   PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QLabel, QPushButton, QGridLayout, QFileDialog, QShortcut
from   PyQt5.QtCore    import Qt, pyqtSlot
from   PyQt5.QtGui     import QKeySequence

# Custom backend functions
import backend         as     bkd

class App(QMainWindow):
   '''Main application.'''

   def __init__(self, iconsPath='icons', *args, **kwargs):
      '''Initialise the application.'''

      super().__init__()


      ###############################
      #        Initial setup        #
      ###############################

      # Script current dir
      self.scriptDir  = opath.dirname(opath.realpath(__file__))

      conf, ok, msg   = bkd.setup(self.scriptDir, 'configuration.yaml')

      if not ok:
         raise IOError(msg)

      # Corpus
      self.corpusDir  = conf['corpusDir']
      self.corpusName = conf['corpusName']
      self.corpusText = conf['corpusText']

      # Icons
      self.icons      = conf['icons']

      # Window and layout
      self.win        = QWidget()
      self.layout     = QGridLayout()
      self.win.setWindowTitle('Jeu des langues (EBTP)')

      ##########################################
      #              Setup widgets             #
      ##########################################

      # Top line input text
      self.inputText  = QLabel('Corpus file')
      self.inputText.setAlignment(Qt.AlignTop)

      # Top line input entry
      self.inputEntry = QLineEdit(self.corpusName)
      self.inputEntry.setAlignment(Qt.AlignTop)
      self.inputEntry.setToolTip('Enter a corpus file name to generate sentences from')

      # Top line input button
      self.inputButton = QPushButton('')
      self.inputButton.setIcon(self.icons['FOLDER'])
      self.inputButton.setFlat(True)
      self.inputButton.setToolTip('Select a corpus text file to generate sentences from')
      self.inputButton.clicked.connect(self.loadCorpus)


      ################################################
      #                 Setup layout                 #
      ################################################

      # First pack of widgets
      self.layout.addWidget(self.inputText,   1, 1)
      self.layout.addWidget(self.inputEntry,  2, 1)
      self.layout.addWidget(self.inputButton, 2, 2)

      self.layout.setAlignment(Qt.AlignTop)
      self.win.setLayout(self.layout)


      ###############################################
      #               Setup shortcuts               #
      ###############################################

      self.shortcuts           = {}
      self.shortcuts['Ctrl+O'] = QShortcut(QKeySequence('Ctrl+O'), self.win)
      self.shortcuts['Ctrl+O'].activated.connect(self.loadCorpus)

      # Show application
      self.win.show()


   #############################################
   #           Corpus related methods          #
   #############################################

   @pyqtSlot()
   def loadCorpus(self, *args, **kwargs):
      '''
      Slot used to load a new corpus file.
      '''

      corpus = self.selectCorpus(*args, **kwargs)

      if corpus is not None:

         # Update corpus properties first (dir, file name and text)
         self._updateCorpusProp(corpus)

         # Update corpus entry widget
         self._changeCorpusEntry(self.corpusName)

      return

   def _updateCorpusProp(self, file, *args, **kwargs):
      '''
      Update corpus properties.

      :param str file: file name to retrieve the text from
      '''

      dir, name = opath.split(file)
      with open(file, 'r') as f:
         text = f.read()

      # Update corpus properties
      self.corpusDir  = dir
      self.corpusName = name
      self.corpusText = text

      return

   def selectCorpus(self, *args, **kwargs):
      '''
      Generate a window to select a corpus text file.

      :rtype: file name if ok, None otherwise
      :rtype: str if ok, None otherwise
      '''

      dialog = QFileDialog(self.win)
      file   = dialog.getOpenFileName(caption='Load a corpus file...', directory=opath.join(self.corpusDir), filter='*.txt')[0]

      if file != '':
         return file
      else:
         return None


   ############################################
   #          Widgets related actions         #
   ############################################

   def _changeCorpusEntry(self, name, *args, **kwargs):
      '''
      Change the corpus entry widget value.
      '''

      self.inputEntry.setText(name)
      return



if __name__ == '__main__':
   root   = QApplication(sys.argv)
   app    = App()
   sys.exit(root.exec_())
