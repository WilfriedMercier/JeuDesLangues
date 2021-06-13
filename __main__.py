# Mercier Wilfried - IRAP

import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import random
import os
import os.path           as     opath

from   PyQt5.QtWidgets   import QMainWindow, QApplication, QDesktopWidget, QWidget, QLineEdit, QLabel, QPushButton, QGridLayout, QFileDialog, QShortcut, QTabWidget, QSpinBox, QGroupBox, QCheckBox, QTreeView, QAbstractItemView
from   PyQt5.QtCore      import Qt, pyqtSlot, QSize
from   PyQt5.QtGui       import QKeySequence, QPalette, QColor, QStandardItemModel, QStandardItem

# Custom backend functions
import backend           as     bkd
import backend.sentences as     snt

class App(QMainWindow):
   '''Main application.'''

   def __init__(self, root, iconsPath='icons', *args, **kwargs):
      '''Initialise the application.'''

      self.root           = root
      super().__init__()

      ###############################
      #        Initial setup        #
      ###############################

      self.rules          = {'Modify_rule' : {},
                             'Other_rule'  : {}
                            }

      # Script current dir
      self.scriptDir      = opath.dirname(opath.realpath(__file__))
      conf, ok, msg       = bkd.setup(self.scriptDir, 'configuration.yaml')

      if not ok:
         raise IOError(msg)

      # Corpus
      self.corpusDir      = conf['corpusDir']
      self.corpusName     = conf['corpus']
      self.corpusText     = snt.make_sentences(conf['corpusText'])

      # Icons
      self.icons          = conf['icons']

      # Language properties
      self.language       = {'vowels' : conf['vowels'], 'consonants' : conf['consonants'], 'map_alternate' : conf['map_alternate'], 'map_alternate_inv' : conf['map_alternate_inv']}

      # Sentence to be modified by the game
      self.sentence       = ''
      self.words          = []
      self.vowels         = []
      self.consonants     = []

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

      self.okPalette      = QPalette()
      self.okColorName    = 'darkgreen'
      green               = QColor(self.okColorName)
      self.okPalette.setColor(QPalette.Text, green)

      self.errorPalette   = QPalette()
      self.errorColorName = 'firebrick'
      red                 = QColor(self.errorColorName)
      self.errorPalette.setColor(QPalette.Text, red)


      ################################################
      #                 Setup layout                 #
      ################################################

      # Main tab widgets layout
      self.layoutMain.setAlignment(Qt.AlignTop)
      self.tabMain.setLayout(self.layoutMain)
      self.tabs.addTab(self.tabMain, "&Game")

      # Game layout
      self._makeLayoutGame()

      # Settings layout
      self._makeLayoutSettings()

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


   ####################################
   #          Layout methods          #
   ####################################

   def _makeLayoutGame(self, *args, **kwargs):
      '''Make the layout for the game tab.'''

      #####################
      #      Widgets      #
      #####################

      # Generate sentence button
      self.genSenButton    = QPushButton()
      self.genSenButton.setFlat(True)
      self.genSenButton.setIcon(self.icons['NEW'])
      self.genSenButton.setIconSize(QSize(24, 24))
      self.genSenButton.setToolTip('Click to randomly draw a new sentence form the corpus')
      self.genSenButton.clicked.connect(self.newSentence)

      # Sentence label
      self.senBox          = QGroupBox('Sentence')
      self.layoutSenbox    = QGridLayout()

      self.senLabel        = QLabel('')
      self.senLabel.setToolTip('Provide and validate a guess to see the sentence.')
      
      # Guess label only shown when the validate button is hit
      self.guessLabel      = QLabel('')
      self.guessLabel.setTextFormat(Qt.RichText)
      
      # Score label
      self.scoreBox        = QGroupBox('Score')
      self.layoutScore     = QGridLayout()
      
      self.scoreLabel      = QLabel('/10')
      self.scoreLabel.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
      self.scoreLabel.setStyleSheet('''font-size: 24px;
                                       font: bold italic "Dyuthi";
                                    ''')
      
      # Play button
      self.playButton      = QPushButton('')
      self.playButton.setFlat(True)
      self.playButton.setIcon(self.icons['PLAY'])
      self.playButton.setIconSize(QSize(24, 24))
      self.playButton.setToolTip('Click to start the game')
      self.playButton.clicked.connect(self.startGame)
      self.playButton.setEnabled(False)
      
      # Treeview with groups sentences
      self.treeview        = QTreeView( )
      self.model           = QStandardItemModel(0, 3)
      self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
      self.treeview.setSelectionMode(QAbstractItemView.NoSelection)
      self.model.setHorizontalHeaderLabels(['Group', 'Turn', 'Sentence'])
      self.treeview.setModel(self.model)
      
      # User guess line
      self.guessEntry      = QLineEdit('')
      self.guessEntry.setAlignment(Qt.AlignTop)
      self.guessEntry.setClearButtonEnabled(True)
      self.guessEntry.isRedoAvailable = True
      self.guessEntry.isUndoAvailable = True
      self.guessEntry.setToolTip('Enter your guess for the mother sentence')
      self.guessEntry.textChanged.connect(self.guessEdited)
      self.guessEntry.setEnabled(False)
      
      # Validate button
      self.validateButton  = QPushButton('')
      self.validateButton.setFlat(True)
      self.validateButton.setIcon(self.icons['VALIDATE'])
      self.validateButton.setIconSize(QSize(24, 24))
      self.validateButton.setToolTip('Click to validate your guess for the mother sentence')
      self.validateButton.clicked.connect(self.validateGame)
      self.validateButton.setEnabled(False)


      #################################
      #             Layout            #
      #################################

      # Generate sentence button
      self.layoutMain.addWidget(self.genSenButton,   1, 1)
      self.layoutMain.addWidget(self.senBox,         1, 2)
      self.layoutMain.addWidget(self.scoreBox,       1, 3)

      # Sentence box widgets
      self.layoutSenbox.addWidget(self.senLabel,     1, 1)
      self.layoutSenbox.addWidget(self.guessLabel,   2, 1)
      self.senBox.setLayout(self.layoutSenbox)
      
      # Score box widgets
      self.layoutScore.addWidget(self.scoreLabel,   1, 1)
      self.scoreBox.setLayout(self.layoutScore)
      
      # Play button
      self.layoutMain.addWidget(self.playButton,     1, 4)

      # User guess line
      self.layoutMain.addWidget(self.guessEntry,     2, 1, 1, 3)
      
      # Validate button
      self.layoutMain.addWidget(self.validateButton, 2, 4)

      # Treeview
      self.layoutMain.addWidget(self.treeview,       3, 1, 1, 4)

      # Column stretch
      self.layoutMain.setColumnStretch(1, 1)
      self.layoutMain.setColumnStretch(3, 1)
      self.layoutMain.setColumnStretch(3, 2)
      self.layoutMain.setColumnStretch(4, 1)
      self.layoutMain.setColumnStretch(2, 10)

      return

   def _makeLayoutSettings(self, *args, **kwargs):
      '''Make the layout for the settings tab.'''

      #####################
      #      Widgets      #
      #####################

      # Top line input text
      self.inputText      = QLabel('Corpus file')
      self.inputText.setAlignment(Qt.AlignTop)

      # Top line input entry
      self.inputEntry = QLineEdit(self.corpusName)
      self.inputEntry.setAlignment(Qt.AlignTop)
      self.inputEntry.setClearButtonEnabled(True)
      self.inputEntry.isRedoAvailable = True
      self.inputEntry.isUndoAvailable = True
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
      self.minwordSpin.setToolTip('Sentences will be drawn from a corpus file with a number of words between the minimum and maximum allowed. The more words, the harder it gets.')
      self.minwordSpin.setSuffix(' words')
      self.minwordSpin.setValue(3)
      self.minwordSpin.setMinimum(1)
      self.minwordSpin.setMaximum(10)
      self.minwordSpin.valueChanged.connect(self._minimumWordsChanged)

      # Second line maximum words text
      self.maxwordText   = QLabel('Maximum number of words')
      self.maxwordText.setAlignment(Qt.AlignTop)

      # Second line maximum words spinbox
      self.maxwordSpin   = QSpinBox()
      self.maxwordSpin.setToolTip('Sentences will be drawn from a corpus file with a number of words between the minimum and maximum allowed. The more words, the harder it gets.')
      self.maxwordSpin.setSuffix(' words')
      self.maxwordSpin.setValue(10)
      self.maxwordSpin.setMinimum(3)
      self.maxwordSpin.valueChanged.connect(self._maximumWordsChanged)

      # Third line group box
      self.rulesBox      = QGroupBox('Rules')
      self.layoutRules   = QGridLayout()

      self.rulesNbGrSpin = QSpinBox()
      self.rulesNbGrSpin.setToolTip('Each group represents a language which will evolve on its own with each new turn')
      self.rulesNbGrSpin.valueChanged.connect(lambda value: self.setRule(nbPlayers = value, which='Other_rule'))
      self.rulesNbGrSpin.setValue(5)
      self.rulesNbGrSpin.setMinimum(1)
      self.rulesNbGrText = QLabel('Number of language groups')

      self.rulesTurnSpin = QSpinBox()
      self.rulesTurnSpin.setToolTip('Players will alter their sentence each turn to simulate the evolution of languages')
      self.rulesTurnSpin.valueChanged.connect(lambda value: self.setRule(nbTurns = value, which='Other_rule'))
      self.rulesTurnSpin.setValue(6)
      self.rulesTurnSpin.setMinimum(1)
      self.rulesTurnText = QLabel('Number of turns')

      self.rulesVow_Vow_S = QCheckBox('Single word vowel to vowel shift')
      self.rulesVow_Vow_S.setToolTip('A vowel will be randomly selected and replaced by another one in a single word')
      self.rulesVow_Vow_S.stateChanged.connect(lambda value: self.setRule(VowtoVow_Single = value == 2, which='Modify_rule'))
      self.rulesVow_Vow_S.setChecked(True)

      self.rulesVow_Vow_A = QCheckBox('All words vowel to vowel shift')
      self.rulesVow_Vow_A.setToolTip('A vowel will be randomly selected and replaced by another one in every word containing that vowel')
      self.rulesVow_Vow_A.stateChanged.connect(lambda value: self.setRule(VowtoVow_All = value == 2, which='Modify_rule'))
      self.rulesVow_Vow_A.setChecked(True)

      self.rulesCon_Con_S  = QCheckBox('Single word consonant to consonant shift')
      self.rulesCon_Con_S.setToolTip('A consonant will be randomly selected and replaced by another one in a single word')
      self.rulesCon_Con_S.stateChanged.connect(lambda value: self.setRule(Con_Con_S = value == 2, which='Modify_rule'))
      self.rulesCon_Con_S.setChecked(True)

      self.rulesCon_Con_A  = QCheckBox('All words consonant to consonant shift')
      self.rulesCon_Con_A.setToolTip('A consonant will be randomly selected and replaced by another one in every word containing that consonant')
      self.rulesCon_Con_A.stateChanged.connect(lambda value: self.setRule(Con_Con_A = value == 2, which='Modify_rule'))
      self.rulesCon_Con_A.setChecked(True)

      self.rulesLet_Let_S  = QCheckBox('Single word letter to letter shift')
      self.rulesLet_Let_S.setToolTip('A letter will be randomly selected and replaced by another one in a single word')
      self.rulesLet_Let_S.stateChanged.connect(lambda value: self.setRule(Let_Let_S = value == 2, which='Modify_rule'))
      self.rulesLet_Let_S.setChecked(True)

      self.rulesLet_Let_A  = QCheckBox('All words letter to letter shift')
      self.rulesLet_Let_A.setToolTip('A letter will be randomly selected and replaced by another one in every word containing that lettter')
      self.rulesLet_Let_A.stateChanged.connect(lambda value: self.setRule(Let_Let_A = value == 2, which='Modify_rule'))
      self.rulesLet_Let_A.setChecked(True)

      self.rulesDel        = QCheckBox('Letter deletion')
      self.rulesDel.setToolTip('A letter will be randomly selected and removed from a single word')
      self.rulesDel.stateChanged.connect(lambda value: self.setRule(Delete = value == 2, which='Modify_rule'))
      self.rulesDel.setChecked(True)

      self.rulesSwap       = QCheckBox('Swap two words')
      self.rulesSwap.setToolTip('Two consecutive words will be randomly selected and interchanged in the sentence')
      self.rulesSwap.stateChanged.connect(lambda value: self.setRule(Swap = value == 2, which='Modify_rule'))
      self.rulesSwap.setChecked(True)


      #################################
      #             Layout            #
      #################################

      # Setting tab widgets layout
      self.layoutSettings.addWidget(self.inputText,   1, 1)
      self.layoutSettings.addWidget(self.inputEntry,  2, 1, 1, 2)
      self.layoutSettings.addWidget(self.inputButton, 2, 3)

      self.layoutSettings.addWidget(self.minwordText, 3, 1)
      self.layoutSettings.addWidget(self.minwordSpin, 4, 1)

      self.layoutSettings.addWidget(self.maxwordText, 3, 2)
      self.layoutSettings.addWidget(self.maxwordSpin, 4, 2)

      self.layoutSettings.addWidget(self.rulesBox,    5, 1, 1, 3)

      # Setting rules box widgets layout
      self.layoutRules.addWidget(self.rulesNbGrSpin,  1,  1)
      self.layoutRules.addWidget(self.rulesNbGrText,  1,  2)

      self.layoutRules.addWidget(self.rulesTurnSpin,  2,  1)
      self.layoutRules.addWidget(self.rulesTurnText,  2,  2)

      self.layoutRules.addWidget(self.rulesVow_Vow_S, 3,  1, 1, 2)
      self.layoutRules.addWidget(self.rulesVow_Vow_A, 4,  1, 1, 2)

      self.layoutRules.addWidget(self.rulesCon_Con_S, 5,  1, 1, 2)
      self.layoutRules.addWidget(self.rulesCon_Con_A, 6,  1, 1, 2)

      self.layoutRules.addWidget(self.rulesLet_Let_S, 7,  1, 1, 2)
      self.layoutRules.addWidget(self.rulesLet_Let_A, 8,  1, 1, 2)

      self.layoutRules.addWidget(self.rulesDel,       9,  1, 1, 2)

      self.layoutRules.addWidget(self.rulesSwap,      10, 1, 1, 2)

      # Setting rules box layout
      self.layoutRules.setAlignment(Qt.AlignTop)
      self.layoutRules.setColumnStretch(1, 1)
      self.layoutRules.setColumnStretch(2, 12)
      self.rulesBox.setLayout(self.layoutRules)

      # Setting tab layout
      self.layoutSettings.setColumnStretch(1, 1)
      self.layoutSettings.setColumnStretch(2, 1)
      self.layoutSettings.setAlignment(Qt.AlignTop)
      self.tabSettings.setLayout(self.layoutSettings)
      self.tabs.addTab(self.tabSettings, "&Settings")

      return
  
    
   ##############################################
   #          Treeview related methods          #
   ##############################################
   
   def addLine(self, name, turn, sentence):
       '''
       Add a line to the treeview.

       :param str name: name of the group
       :param int turn: turn corresponding to the given sentence
       :param str sentence: sentence to show in the treeview
       '''
       
       # Root item
       rootNode = self.model.invisibleRootItem()
       
       # Define Items
       name     = QStandardItem(name)
       turn     = QStandardItem('%d' %turn)
       sentence = QStandardItem(sentence)
       item     = (name, turn, sentence)
       
       # Append line to the treeview
       rootNode.appendRow(item) 
       
       return


   ############################################
   #           Game related methods           #
   ############################################

   def newSentence(self, *args, **kwargs):
      '''Actions taken when the new sentence button is pressed.'''

      # Update sentence
      self.sentence, self.words, nb = snt.pick_sentence(self.corpusText, self.minwordSpin.value(), self.maxwordSpin.value())
      sentence_split                = self.sentence.split(' ')
      if sentence_split[0] in ['--', '-']:
           self.sentence            = self.sentence[len(sentence_split[0])+1:]
      
      # Update label
      self.senLabel.setText('*' * len(self.sentence))
      
      # Update label
      if nb <= 1:
          word = 'word'
      else:
          word = 'words'
          
      self.senBox.setTitle('Selected sentence - %d %s' %(nb, word))
      self.resetGame()
      
      # Extract vowels and consonants from sentence
      self.vowels, self.consonants  = snt.make_vowels_consonants(self.sentence, self.language)
      
      return
  
    
   def resetGame(self, *args, **kwargs):
       '''Reset the interface and properties related to the game.'''
       
       # Clear treeview
       self.model.removeRows(0, self.model.rowCount())
       
       # Clear guess label
       self.guessLabel.setText('')
       
       # Enable start game button and disable following buttons
       self.playButton.setEnabled(True)
       self.guessEntry.setEnabled(False)
       self.validateButton.setEnabled(False)
       
       # Reset score
       self.scoreLabel.setText('/10')
       
       return
  
    
   def startGame(self, *args, **kwargs):
       '''Start the game.'''
       
       # Create as many groups as necessary
       nbGroups     = self.rulesNbGrSpin.value()
       groups       = [bkd.LanguageGroup(self.sentence, self.language, self.vowels, self.consonants, idd='Group %d' %i) for i in range(1, nbGroups+1)]
       
       # Loop through each turn
       nbTurns      = self.rulesTurnSpin.value()
       for i in range(nbTurns):
           
           # Pick a rule (we will remove the loop once we've included all the methods)
           rule     = random.choice(list(self.rules['Modify_rule'].keys()))
           while rule not in ['VowtoVow_All', 'VowtoVow_Single']:
               rule = random.choice(list(self.rules['Modify_rule'].keys()))
           
           # Loop through each group
           for group in groups:
               msg  = group.applyRule(rule)
               print(msg)
               print('Sentence:', group.sentence[-1])
               print('Vowels:', group.vowels)
               
       # Add each group to the treeview
       for group in groups:
           name     = group.id
           turn     = len(group.sentence)-1
           sentence = group.sentence[-1]
           
           self.addLine(name, turn, sentence)
           
       # Avoid users launching another batch again
       self.playButton.setEnabled(False)
       
       # Let the user give their answer
       self.guessEntry.setEnabled(True)
       
       return
   
    
   def setScore(self, score, *args, **kwargs):
       '''
       Set the score.

       :param float score: score
       '''
       
       strScore     = '%.1f' %score
       if strScore[-2:] == '.0':
           strScore = strScore[:-2]
       
       if score < 5:
           text     = self.setBadText(strScore)
       elif score > 7:
           text     = self.setOkText(    strScore)
       else:
           text     = self.setMediumText(   strScore)
           
       self.scoreLabel.setText(text + '/10')
       return
   
    
   def validateGame(self, *args, **kwargs):
       '''Actions taken when the validate button is hit.'''
       
       # User sentence split in words, but keeping characters such as ,
       sentence                      = self.guessEntry.text()
       sentence_split                = sentence.split(' ')
       sentence_rec                  = ''
       
       # Words from the user guess
       words                         = snt.make_words(sentence)
       
       score                         = 0
       
       for guess, true, full in zip(words, self.words, sentence_split):
           
           # Split full word to only keep the word part of it
           full_split                = full.partition(guess)
           
           for pos in range(3):
               
               # We only colorise the word, not the characters around
               if pos != 1:
                   sentence_rec     += full_split[pos]
               else:
       
                   # If guess is similar to the word, we apply ok color, else we apply bad color
                   if guess.lower() == true.lower():
                       sentence_rec += self.setOkText(full_split[pos])
                       score        += 1
                   else:
                       sentence_rec += self.setBadText(full_split[pos])
                       
           sentence_rec             += ' '
           
       # Need to deal with punctuation at the end
       if sentence_split[-1] in ['!', '?', '.', ',', ';', ':'] and sentence_split[-1] != sentence_rec[-2]:
           sentence_rec             += sentence_split[-1]
       
       self.senLabel.setText(self.sentence)
       self.guessLabel.setText(sentence_rec)
       self.guessEntry.setText('')
       
       # Set score
       self.setScore(score/len(self.words)*10)
       
       return


   #############################################
   #           Corpus related methods          #
   #############################################

   def _changeCorpusEntry(self, name, *args, **kwargs):
      '''
      Change the corpus entry widget value.

      :param str name: corpus name
      '''

      self.inputEntry.setText(name)
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
     
   def guessEdited(self, text, *args, **kwargs):
       '''Actions taken when the guess is edited.'''
       
       if text != '':
           self.validateButton.setEnabled(True)
       else:
           self.validateButton.setEnabled(False)
           
       return
   
   def setBadText(self, text, *args, **kwargs):
       '''
       Transform a text into rich text with a red color.

       :param str text: plain text
       
       :returns: html formatted text
       :rtype: str
       '''
       
       return '<font color="%s">%s</font>' %(self.errorColorName, text)
   
   def setMediumText(self, text, *args, **kwargs):
       '''
       Transform a text into rich text with an orange color.

       :param str text: plain text
       
       :returns: html formatted text
       :rtype: str
       '''
       
       return '<font color="darkorange">%s</font>' %text

   def setOkText(self, text, *args, **kwargs):
       '''
       Transform a text into rich text with a green color.

       :param str text: plain text
       
       :returns: html formatted text
       :rtype: str
       '''
       
       return '<font color="%s">%s</font>' %(self.okColorName, text)

   def setRule(self, which=None, **kwargs):
      '''
      Set a rule with the given value. Function should be called as follows

      ... self.setRule(someRule = someValue, which='Other_rule')
      '''
      
      if which is None:
          raise ValueError('which parameter must not be None to set a rule.')
        
      for item, value in kwargs.items():
          self.rules[which][item] = value

      return


if __name__ == '__main__':
   root   = QApplication(sys.argv)
   app    = App(root)
   sys.exit(root.exec_())
