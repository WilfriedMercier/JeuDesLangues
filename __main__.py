# Mercier Wilfried - IRAP

import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import os
import os.path         as     opath

from   PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QLabel, QPushButton, QGridLayout
from   PyQt5.QtGui     import QIcon, QBitmap
from   PyQt5.QtCore    import Qt, pyqtSlot

# Custom backend functions
import backend         as     bkd

class App(QMainWindow):
   '''Main application.'''

   def __init__(self, iconsPath='icons', *args, **kwargs):
      '''Initialise the application.'''

      super().__init__()

      # Script current dir
      self.scriptDir  = opath.dirname(opath.realpath(__file__))

      # Setup program icons
      conf, ok        = bkd.loadIcons(iconsPath=iconsPath)

      if not ok:
         raise IOError('You are missing the %s directory which contains program icons.' %iconsPath)
      else:
         for key, value in conf.items():
            conf[key] = QIcon(QBitmap(value))

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
      self.inputEntry = QLineEdit('')
      self.inputEntry.setAlignment(Qt.AlignTop)
      self.inputEntry.setToolTip('Enter a valide corpus file name to generate sentences from')

      # Top line input button
      self.inputButton = QPushButton('')
      self.inputButton.setToolTip('Select a corpus text file to generate sentences from')
      self.inputButton.clicked.connect(self.selectCorpus)


      ################################################
      #                 Setup layout                 #
      ################################################

      # First pack of widgets
      self.layout.addWidget(self.inputText,   1, 1)
      self.layout.addWidget(self.inputEntry,  2, 1)
      self.layout.addWidget(self.inputButton, 2, 2)

      self.layout.setAlignment(Qt.AlignTop)
      self.win.setLayout(self.layout)

      # Show application
      self.win.show()


   @pyqtSlot()
   def selectCorpus(self, *args, **kwargs):
      '''Generate  window to select a corpus text file.'''

      print('Clicked')
      return

if __name__ == '__main__':
   root   = QApplication(sys.argv)
   app    = App()
   sys.exit(root.exec_())
