# Mercier Wilfried - IRAP

import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from   PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QLabel, QGridLayout
from   PyQt5.QtCore    import Qt

class App(QMainWindow):
   '''Main application.'''

   def __init__(self, *args, **kwargs):
      '''Initialise the application.'''

      super().__init__()
      self.setWindowTitle('Jeu des langues (EBTP)')

      # Window and layout
      self.win        = QWidget()
      self.layout     = QGridLayout()


      ##########################################
      #              Setup widgets             #
      ##########################################

      # Top line input text
      self.inputText  = QLabel('Corpus file')
      self.inputText.setAlignment(Qt.AlignTop)

      # Top line input entry
      self.inputEntry = QLineEdit('')
      self.inputEntry.setAlignment(Qt.AlignTop)


      ################################################
      #                 Setup layout                 #
      ################################################

      self.layout.addWidget(self.inputText,  1, 1)
      self.layout.addWidget(self.inputEntry, 2, 1)
      self.layout.setAlignment(Qt.AlignTop)
      self.win.setLayout(self.layout)

      # Show application
      self.win.show()

if __name__ == '__main__':
   root   = QApplication(sys.argv)
   app    = App()
   sys.exit(root.exec_())
