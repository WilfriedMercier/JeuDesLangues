# Mercier Wilfried - IRAP

import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import os
import os.path         as     opath

from   PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QWidget, QLineEdit, QLabel, QPushButton, QGridLayout, QFileDialog, QShortcut, QTabWidget, QSpinBox
from   PyQt5.QtCore    import Qt, pyqtSlot
from   PyQt5.QtGui     import QKeySequence, QPalette, QColor

# Custom backend functions
import backend         as     bkd

class App(QMainWindow):
   '''Main application.'''

   def __init__(self, root, iconsPath='icons', *args, **kwargs):
      '''Initialise the application.'''

      self.root       = root
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

      # Window
      self.win            = QWidget()
      self.win.setWindowTitle('Jeu des langues (EBTP)')
      self.layoutWin      = QGridLayout()

      # Tabs
      self.tabs           = QTabWidget()

      self.tabMain        = QWidget()
      self.layoutMain     = QGridLayout()

      self.tabSettings    = QWidget()
      self.layoutSettings = QGridLayout()


      ############################################
      #           Common color palettes          #
      ############################################

      self.okPalette    = QPalette()
      green             = QColor('darkgreen')
      self.okPalette.setColor(QPalette.Text, green)

      self.errorPalette = QPalette()
      red             = QColor('firebrick')
      self.errorPalette.setColor(QPalette.Text, red)

      #############################################
      #              Settings widgets             #
      #############################################

      # Top line input text
      self.inputText  = QLabel('Corpus file')
      self.inputText.setAlignment(Qt.AlignTop)

      # Top line input entry
      self.inputEntry = QLineEdit(self.corpusName)
      self.inputEntry.setAlignment(Qt.AlignTop)
      self.inputEntry.setToolTip('Enter a corpus file name to generate sentences from')
      self.inputEntry.setPalette(self.okPalette)
      self.inputEntry.textEdited.connect(self.checkAndLoadCorpus)

      # Top line input button
      self.inputButton = QPushButton('')
      self.inputButton.setIcon(self.icons['FOLDER'])
      self.inputButton.setFlat(True)
      self.inputButton.setToolTip('Select a corpus text file to generate sentences from')
      self.inputButton.clicked.connect(self.loadCorpus)

      # Second line minimum words text
      self.minwordText = QLabel('Minimum number of words')
      self.minwordText.setAlignment(Qt.AlignTop)

      # Second line minimum words spinbox
      self.minwordSpin = QSpinBox()
      self.minwordSpin.setSuffix(' words')
      self.minwordSpin.setValue(3)
      self.minwordSpin.setMinimum(1)
      self.minwordSpin.setMaximum(10)
      self.minwordSpin.valueChanged.connect(self._minimumWordsChanged)

      # Second line maximum words text
      self.maxwordText = QLabel('Maximum number of words')
      self.maxwordText.setAlignment(Qt.AlignTop)

      # Second line maximum words spinbox
      self.maxwordSpin = QSpinBox()
      self.maxwordSpin.setSuffix(' words')
      self.maxwordSpin.setValue(10)
      self.maxwordSpin.setMinimum(3)
      self.maxwordSpin.valueChanged.connect(self._maximumWordsChanged)

      ################################################
      #                 Setup layout                 #
      ################################################

      # Main tab widgets layout
      self.layoutMain.setAlignment(Qt.AlignTop)
      self.tabMain.setLayout(self.layoutMain)
      self.tabs.addTab(self.tabMain, "&Game")

      # Settings tab widgets layout
      self.layoutSettings.addWidget(self.inputText,   1, 1)
      self.layoutSettings.addWidget(self.inputEntry,  2, 1, 1, 2)
      self.layoutSettings.addWidget(self.inputButton, 2, 3)

      self.layoutSettings.addWidget(self.minwordText, 3, 1)
      self.layoutSettings.addWidget(self.minwordSpin, 4, 1)

      self.layoutSettings.addWidget(self.maxwordText, 3, 2)
      self.layoutSettings.addWidget(self.maxwordSpin, 4, 2)

      self.layoutSettings.setColumnStretch(1, 1)
      self.layoutSettings.setColumnStretch(2, 1)
      self.layoutSettings.setAlignment(Qt.AlignTop)
      self.tabSettings.setLayout(self.layoutSettings)
      self.tabs.addTab(self.tabSettings, "&Settings")

      # Main window layout
      self.layoutWin.addWidget(self.tabs, 1, 1)
      self.win.setLayout(self.layoutWin)

      ###############################################
      #               Setup shortcuts               #
      ###############################################

      self.shortcuts           = {}
      self.shortcuts['Ctrl+O'] = QShortcut(QKeySequence('Ctrl+O'), self.win)
      self.shortcuts['Ctrl+O'].activated.connect(self.loadCorpus)

      # Show application
      self.win.resize(800, 800)
      self.win.show()
      self.centre()


   #############################################
   #           Corpus related methods          #
   #############################################

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

   def errorCorpus(self, *args, **kwargs):
      '''Fonction called when the corpus file is not ok.'''

      self.inputEntry.setPalette(self.errorPalette)
      return

   def checkAndLoadCorpus(self, file, *args, **kwargs):
      '''Check that a corpus file and load it if it is fine.'''

      if opath.isfile(file) and file.split('.')[-1]:
         self._updateCorpusProp(file)
         self.okCorpus()
      else:
         self.errorCorpus()

      return

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

   def okCorpus(self, *args, **kwargs):
      '''Fonction called when the corpus file is ok.'''

      self.inputEntry.setPalette(self.okPalette)
      return

   def selectCorpus(self, *args, **kwargs):
      '''
      Generate a window to select a corpus text file.

      :rtype: file name if ok, None otherwise
      :rtype: str if ok, None otherwise
      '''

      dialog = QFileDialog(self.win)
      file   = dialog.getOpenFileName(caption='Load a corpus file...', directory=opath.join(self.corpusDir), filter='*.txt')[0]

      if self.checkFile(file):
         return file
      else:
         return None


   ####################################
   #          Number of words         #
   ####################################

   def _minimumWordsChanged(self, value, *args, **kwargs):
      '''Actions taken when the minimum number of words changed.'''

      if value == 1:
         self.minwordSpin.setSuffix(' word')
      else:
         self.minwordSpin.setSuffix(' words')

      self.maxwordSpin.setMinimum(value)
      return


   def _maximumWordsChanged(self, value, *args, **kwargs):
      '''Actions taken when the maximum number of words changed.'''

      if value == 1:
         self.maxwordSpin.setSuffix(' word')
      else:
         self.maxwordSpin.setSuffix(' words')
      self.minwordSpin.setMaximum(value)
      return


   ############################################
   #          Widgets related actions         #
   ############################################

   def _changeCorpusEntry(self, name, *args, **kwargs):
      '''
      Change the corpus entry widget value.

      :param str name: corpus name
      '''

      self.inputEntry.setText(name)
      return


   ##################################
   #          Miscellaneous         #
   ##################################

   def centre(self, *args, **kwargs):
      '''Centre the window.'''

      frameGm     = self.frameGeometry()
      screen      = self.root.desktop().screenNumber(self.root.desktop().cursor().pos())
      centerPoint = self.root.desktop().screenGeometry(screen).center()
      centerPoint.setY(centerPoint.y() - 100)
      centerPoint.setX(centerPoint.x() - 100)
      frameGm.moveCenter(centerPoint)
      self.win.move(frameGm.topLeft())

      return

   def checkFile(self, file, *args, **kwargs):
      '''
      Check that the given file exists.

      :param str file: file to check

      :returns: True if file exists, False otherwise
      :rtype: boolean
      '''

      if opath.isfile(file):
         return True
      else:
         return False

if __name__ == '__main__':
   root   = QApplication(sys.argv)
   app    = App(root)
   sys.exit(root.exec_())
