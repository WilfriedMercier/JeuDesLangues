# Mercier Wilfried - IRAP

import time
import copy
import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import random
import os
import os.path               as     opath

from   PyQt5.QtWidgets       import QMainWindow, QApplication, QMenuBar, QAction, QDesktopWidget, QWidget, QLineEdit, QLabel, QPushButton, QGridLayout, QVBoxLayout, QFileDialog, QShortcut, QTabWidget, QSpinBox, QGroupBox, QCheckBox, QTreeView, QAbstractItemView, QStatusBar, QSplashScreen
from   PyQt5.QtCore          import Qt, pyqtSlot, QSize, QEventLoop
from   PyQt5.QtGui           import QKeySequence, QPalette, QColor, QStandardItemModel, QStandardItem, QFont, QPixmap

# Custom backend functions
import backend               as     bkd
import backend.sentences     as     snt

class App(QMainWindow):
   '''Main application.'''

   def __init__(self, root, iconsPath='icons', *args, **kwargs):
      '''Initialise the application.'''
      
      self.root               = root
      super().__init__()
      self.setWindowTitle('Jeu des langues (EBTP)')
      
      # Script current dir
      self.scriptDir          = opath.dirname(opath.realpath(__file__))

      
      ###################################
      #       Setup splash screen       #
      ###################################
      
      self.splash             = QSplashScreen(QPixmap(opath.join(self.scriptDir, 'background.png')))
      self.splash.show()
      self.splashlabel        = QLabel('Test')
      self.splashlabel.setAlignment(Qt.AlignCenter)
      self.splashlabel.setStyleSheet('''
                                     font-size: 12px;
                                     font: bold italic;
                                    ''')
      
      self.splashlayout       = QVBoxLayout()
      self.splashlayout.addSpacing(350)
      self.splashlayout.addWidget(self.splashlabel)
      self.splash.setLayout(self.splashlayout)
   
      # Let enough time for the event loop to catch the opening of the background image
      time.sleep(0.1)
      self.root.processEvents()
      
      try:
   
         ###############################
         #        Initial setup        #
         ###############################
   
         conf, ok, msg       = bkd.setup(self.scriptDir, 'configuration.yaml', parent=self)
   
         if not ok:
            raise IOError(msg)
            
         # Rules
         self.rules          = conf['rules']
   
         # Corpus
         self.corpusName     = conf['corpus']
         self.corpusText     = snt.make_sentences(conf['corpusText'])
   
         # Icons
         self.icons          = conf['icons']
   
         # Language properties
         self.languageName   = conf['language']
         self.langAlteration = conf['languageAlterations']
         self.language       = {'vowels'            : conf['vowels'], 
                                'consonants'        : conf['consonants'], 
                                'map_alternate'     : conf['map_alternate'], 
                                'map_alternate_inv' : conf['map_alternate_inv']
                               }
   
         # Sentence to be modified by the game
         self.sentence       = ''
         self.words          = []
         self.vowels         = []
         self.consonants     = []
         
         # Interface language
         self.translations   = conf['translations']
         translation         = conf['trans_name']
         self.currentTrans   = None
         self.trans_prop     = conf['trans_prop']
         self.old_trans_prop = None
   
         self.splashlabel.setText('Setting interface...')
         self.root.processEvents()
   
         # Window
         self.win            = QWidget()
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
         self.tabs.addTab(self.tabMain, "")
         
         # Game layout
         self.splashlabel.setText('Drawing game tab...')
         self.root.processEvents()
         self._makeLayoutGame()
   
         # Settings layout
         self.splashlabel.setText('Drawing game tab...')
         self.root.processEvents()
         self._makeLayoutSettings()
         
         # Setup settings widgets state
         self.splashlabel.setText('Setup default settings...')
         self.root.processEvents()
         self._setupSettings()
         
         # Grey out save button
         self.saveButton.setEnabled(False)
         
         # Connect widgets to setting rules
         self.rulesNbGrSpin.valueChanged.connect( lambda value: self.setRule(nbPlayers = value,            which='Other_rule'))
         self.rulesTurnSpin.valueChanged.connect( lambda value: self.setRule(nbTurns = value,              which='Other_rule'))
         self.rulesVow_Vow_S.stateChanged.connect(lambda value: self.setRule(VowtoVow_Single = value == 2, which='Modify_rule'))
         self.rulesVow_Vow_A.stateChanged.connect(lambda value: self.setRule(VowtoVow_All = value == 2,    which='Modify_rule'))
         self.rulesCon_Con_S.stateChanged.connect(lambda value: self.setRule(ContoCon_Single = value == 2, which='Modify_rule'))
         self.rulesCon_Con_A.stateChanged.connect(lambda value: self.setRule(ContoCon_All = value == 2,    which='Modify_rule'))
         self.rulesLet_Let_S.stateChanged.connect(lambda value: self.setRule(LettoLet_Single = value == 2, which='Modify_rule'))
         self.rulesLet_Let_A.stateChanged.connect(lambda value: self.setRule(LettoLet_All = value == 2,    which='Modify_rule'))
         self.rulesDel.stateChanged.connect(      lambda value: self.setRule(Delete = value == 2,          which='Modify_rule'))
         self.rulesSwap.stateChanged.connect(     lambda value: self.setRule(Swap = value == 2,            which='Modify_rule'))
   
         # Main window layout
         self.layoutWin.addWidget(self.tabs, 1, 1)
         self.win.setLayout(self.layoutWin)
         
         # Status bar
         self.splashlabel.setText('Drawing status bar...')
         self.root.processEvents()
         
         font              = QFont()
         font.setPointSize(8)
         self.statusbar    = QStatusBar()
         self.statusbar.setMaximumHeight(12)
         self.statusbar.setFont(font)
         self.layoutWin.addWidget(self.statusbar, 2, 1)
         
         
         #####################################################
         #                 Apply translation                 #
         #####################################################
         
         self.splashlabel.setText('Translate interface...')
         self.root.processEvents()
         
         self._setupTranslation()
         self.translate(None)
         self.currentTrans        = translation
         
         # Set treview section properties
         self.treeview.header().setDefaultAlignment(Qt.AlignHCenter)
         self.treeview.header().resizeSection(0, 100)
         self.treeview.header().resizeSection(1, 50)
   
   
         ###############################################
         #               Setup shortcuts               #
         ###############################################
   
         self.shortcuts           = {}
         self.shortcuts['Ctrl+O'] = QShortcut(QKeySequence('Ctrl+O'), self.tabSettings)
         self.shortcuts['Ctrl+O'].activated.connect(self.loadCorpus)
         
         self.shortcuts['Ctrl+R'] = QShortcut(QKeySequence('Ctrl+R'), self.tabMain)
         self.shortcuts['Ctrl+R'].activated.connect(self.newSentence)
   
         self.shortcuts['Ctrl+P'] = QShortcut(QKeySequence('Ctrl+P'), self.tabMain)
         self.shortcuts['Ctrl+P'].activated.connect(self.startGame)
         
   
         ############################
         #           Menu           #
         ############################
         
         self.splashlabel.setText('Setting menu...')
         self.root.processEvents()
      
         menubar           = self.menuBar()
         transmenu         = menubar.addMenu('&Interface')
         
         # Setup actions given the languages found
         for t in self.translations:
             tbase         = opath.basename(t)
             action        = QAction('&%s' %tbase.split('.yaml')[0], self)
             action.triggered.connect(lambda *args, x=tbase: self.translate(x))
             
             transmenu.addAction(action)
      finally:
         self.splash.finish(self)

         # Show application
         self.setCentralWidget(self.win)
         self.resize(800, 800)
         self.show()
         self.centre()
         
         self.statusbar.showMessage('Initialisation complete')
      
      
   #########################################################################
   #         Mapping interface translation to objects and commands         #
   #########################################################################
      
   def _setupTranslation(self, *args, **kwargs):
      '''Setup the translation properties. Must only be run once at startup.'''
      
      # These map names appearing in the translation file with Qt method names
      self.setMethods = {'tooltip' : 'setToolTip',
                         'text'    : 'setText',
                         'title'   : 'setTitle',
                         'headers' : 'setHorizontalHeaderLabels',
                         'tabtext' : 'setTabText'
                        }
      return
   
   
   def applyTranslation(self, objName, methodName, values):
      '''
      Apply a translation to an object using the setMethods dict.
      
      :param str objName: oject name as appearing in the translation file
      :param str methodName: method name as appearing in the translation file
      :param list values: values to apply to the object, they will be passed as *values
      
      :returns: 
         * 0 if everything is fine
         * -1 if object name is not an attribute
         * -2 if object method does not exist
      
      '''
      
      # Get object and method
      try:
         obj    = getattr(self, objName)
      except AttributeError:
         return -1
      
      try:
         method = getattr(obj, methodName)
      except AttributeError:
         return -2
      
      # Apply method
      method(*values)
      
      return 0
   
   def translate(self, newTransName, *args, **kwargs):
      '''
      Translate the interface using the currently loaded translation file.
      
      :param str newTransName: name of the new translation. If None or if similar to previous translation, no change is applied.
      '''
      
      def check(obj, method, val):
         '''
         Apply translation and check that nothing went wrong.

         :param obj: object to apply the translation to
         :param method: method used to apply the translation
         :parm list val: list of parameters to pass to the method

         :raises AttributeError:
            * if the method could be found in object
            * if the object could not be found
         '''
         
         err = self.applyTranslation(obj, method, val)
                  
         # This error should never be raised in theory
         if err == -2:
            raise AttributeError('Method %s could not be found in object %s.' %(method, obj))
            
         # This means we are dealing with objects which are not attributes
         elif err == -1:
            raise AttributeError('Object %s could not be found.' %obj) 
            
         return
      
      
      # Translation at startup
      if newTransName is None:
         for obj, value in self.trans_prop.items():
            
            # Skip objects which do not correspond to attributes
            if obj in ['word', 'selectCorpus']:
               continue
            
            # An object can have various methods to apply
            for method, val in value.items():
               
               # Skip some methods if we do not need to apply them
               if obj in ['minwordSpin', 'maxwordSpin'] and method == 'suffix':
                  continue
               
               # Update tabs one by one
               elif obj == 'tabs' and method == 'tabtext':
                  method            = self.setMethods[method]
                  
                  for index, name in val.items():
                     val            = [index, name]
                     check(obj, method, val)
                  continue
               
               # We must pass parameters as a list
               if not isinstance(val, list):
                  val               = [val]
                  
               method = self.setMethods[method]
               check(obj, method, val)
               
                     
      # Translation if interface is already drawn with a language
      else:
         
         transNameNoSuffix            = newTransName.split('.yaml')[0]
         
         # If user picked the same translation, do nothing
         if transNameNoSuffix != self.currentTrans:
            
            # By default, we assume no translation file could be found
            ok                        = False
            
            # Find translation in translations list
            for transFile in self.translations:
               if newTransName == opath.basename(transFile):
                     
                  # Save old translation before overwriting with new one
                  self.old_trans_prop = self.trans_prop
                  self.trans_prop     = bkd.setupTranslation(transFile)
                  ok                  = True
                  break
            
            # Check that a tranlation was found
            if not ok:
               raise IOError('No translation %s was found in translation files list %s' %(newTransName, self.translations))
               
            # Loop through objects
            for obj, value in self.trans_prop.items():
               
               # Skip selectCorpus because it will be updated when calling the open window, word is used later on
               if obj in ['word', 'selectCorpus']:
                  continue
               
               # An object can have various methods to apply
               for method, val in value.items():
                  
                  # Update spinboxes using same value to update word according to the singular or plural form in use
                  if obj in ['minwordSpin', 'maxwordSpin'] and method == 'suffix':
                     if obj == 'minwordSpin':
                        self._minimumWordsChanged(self.minwordSpin.value())
                     else:
                        self._maximumWordsChanged(self.maxwordSpin.value())
                     continue
                        
                  # Update sentence box label
                  elif obj == 'senBox' and method == 'title':
                     
                     # Get old sentence
                     val               = self.senBox.title()
                     
                     # Replace the sentence word
                     val               = val.replace(self.old_trans_prop['senBox']['title'], self.trans_prop['senBox']['title'])
                     
                     # Replace the additional word part
                     if self.old_trans_prop['word']['plural'] in val:
                        val            = val.replace(self.old_trans_prop['word']['plural'], self.trans_prop['word']['plural'])
                     elif self.old_trans_prop['word']['singular'] in val:
                        val            = val.replace(self.old_trans_prop['word']['singular'], self.trans_prop['word']['singular'])
                     
                  # Update tabs one by one
                  elif obj == 'tabs' and method == 'tabtext':
                     method            = self.setMethods[method]
                     
                     for index, name in val.items():
                        val            = [index, name]
                        check(obj, method, val)
                     continue
                     
                  # We must pass parameters as a list
                  if not isinstance(val, list):
                     val               = [val]
                     
                  method               = self.setMethods[method]
                  check(obj, method, val)
                  self.currentTrans    = transNameNoSuffix
      
            self.statusbar.showMessage('Translated interface to %s' %self.currentTrans)
   
      return
               

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
      self.genSenButton.clicked.connect(self.newSentence)

      # Sentence label
      self.senBox          = QGroupBox('')
      self.layoutSenbox    = QGridLayout()

      self.senLabel        = QLabel('')
      
      # Guess label only shown when the validate button is hit
      self.guessLabel      = QLabel('')
      self.guessLabel.setTextFormat(Qt.RichText)
      
      # Score label
      self.scoreBox        = QGroupBox('')
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
      self.playButton.clicked.connect(self.startGame)
      self.playButton.setEnabled(False)
      
      # Treeview with groups sentences
      self.treeview        = QTreeView()
      self.model           = QStandardItemModel(0, 3)
      self.treeview.setAnimated(True)
      self.treeview.setItemsExpandable(True)
      self.treeview.setExpandsOnDoubleClick(True)
      self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
      self.treeview.setSelectionMode(QAbstractItemView.NoSelection)
      self.treeview.setModel(self.model)
      self.treeview.header().setStretchLastSection(True)
      
      # User guess line
      self.guessEntry      = QLineEdit('')
      self.guessEntry.setAlignment(Qt.AlignTop)
      self.guessEntry.setClearButtonEnabled(True)
      self.guessEntry.isRedoAvailable = True
      self.guessEntry.isUndoAvailable = True
      self.guessEntry.textChanged.connect(self.guessEdited)
      self.guessEntry.returnPressed.connect(self.validateGame)
      self.guessEntry.setEnabled(False)
      
      # Validate button
      self.validateButton  = QPushButton('')
      self.validateButton.setFlat(True)
      self.validateButton.setIcon(self.icons['VALIDATE'])
      self.validateButton.setIconSize(QSize(24, 24))
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
      self.inputText     = QLabel('')
      self.inputText.setAlignment(Qt.AlignTop)

      # Top line input entry
      self.inputEntry    = QLineEdit(self.corpusName)
      self.inputEntry.setAlignment(Qt.AlignTop)
      self.inputEntry.setClearButtonEnabled(True)
      self.inputEntry.isRedoAvailable = True
      self.inputEntry.isUndoAvailable = True
      self.inputEntry.setPalette(self.okPalette)
      self.inputEntry.textEdited.connect(self.checkAndLoadCorpus)

      # Top line input button
      self.inputButton    = QPushButton('')
      self.inputButton.setIcon(self.icons['FOLDER'])
      self.inputButton.setFlat(True)
      self.inputButton.clicked.connect(self.loadCorpus)

      # Second line minimum words text
      self.minwordText    = QLabel('')
      self.minwordText.setAlignment(Qt.AlignTop)

      # Second line minimum words spinbox
      self.minwordSpin    = QSpinBox()
      self.minwordSpin.setMinimum(1)
      self.minwordSpin.setMaximum(10)

      # Second line maximum words text
      self.maxwordText    = QLabel('')
      self.maxwordText.setAlignment(Qt.AlignTop)

      # Second line maximum words spinbox
      self.maxwordSpin    = QSpinBox()
      self.maxwordSpin.setMinimum(3)
      
      self.minwordSpin.valueChanged.connect(self._minimumWordsChanged)
      self.maxwordSpin.valueChanged.connect(self._maximumWordsChanged)
      self.minwordSpin.setValue(3)
      self.maxwordSpin.setValue(10)
      
      # Third line group box
      self.rulesBox       = QGroupBox('')
      self.layoutRules    = QGridLayout()

      self.rulesNbGrSpin  = QSpinBox()
      self.rulesNbGrSpin.setMinimum(1)
      
      self.rulesNbGrText  = QLabel('')

      self.rulesTurnSpin  = QSpinBox()
      self.rulesTurnSpin.setMinimum(1)
      
      self.rulesTurnText  = QLabel('')
      self.rulesVow_Vow_S = QCheckBox('')
      self.rulesVow_Vow_A = QCheckBox('')
      self.rulesCon_Con_S = QCheckBox('')
      self.rulesCon_Con_A = QCheckBox('')
      self.rulesLet_Let_S = QCheckBox('')
      self.rulesLet_Let_A = QCheckBox('')
      self.rulesDel       = QCheckBox('')
      self.rulesSwap      = QCheckBox('')
      
      # Fourth line save button
      self.saveButton      = QPushButton('')
      self.saveButton.setFlat(True)
      self.saveButton.setIcon(self.icons['SAVE'])
      self.saveButton.setIconSize(QSize(24, 24))
      self.saveButton.clicked.connect(self.saveSettings)


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
      
      # Setting save button layout
      self.layoutSettings.addWidget(self.saveButton, 6, 3)

      # Setting tab layout
      self.layoutSettings.setColumnStretch(1, 1)
      self.layoutSettings.setColumnStretch(2, 1)
      
      for i in range(1, 7):
         if i == 5:
            self.layoutSettings.setRowStretch(i, 30)
         else:
            self.layoutSettings.setRowStretch(i, 1)
            
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
       name.setTextAlignment(Qt.AlignHCenter)
       
       turn     = QStandardItem('%d' %turn)
       turn.setTextAlignment(Qt.AlignHCenter)
       
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
          word                      = self.trans_prop['word']['singular']
      else:
          word                      = self.trans_prop['word']['plural']
          
      self.senBox.setTitle('%s - %d %s' %(self.trans_prop['senBox']['title'], nb, word))
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
       groups       = [bkd.LanguageGroup(self.sentence, self.language, self.vowels, self.consonants, idd='%s %d' %(self.trans_prop['model']['headers'][0], i)) for i in range(1, nbGroups+1)]
       
       # Loop through each turn
       nbTurns      = self.rulesTurnSpin.value()
       for i in range(nbTurns):
           
           # Pick a rule (we will remove the loop once we've included all the methods)
           print(self.rules['Modify_rule'])
           print([key for key, value in self.rules['Modify_rule'].items() if value])
           rule     = random.choice(list(self.rules['Modify_rule'].keys()))
           while rule not in ['VowtoVow_All', 'VowtoVow_Single', 'ContoCon_All', 'ContoCon_Single', 'Swap']:
               rule = random.choice(list(self.rules['Modify_rule'].keys()))
           
           # Loop through each group
           for group in groups:
               msg  = group.applyRule(rule)
               print(msg)
               
           
               
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
       
       # Place focus on the entry widget
       self.guessEntry.setFocus()
       
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
      file   = dialog.getOpenFileName(caption=self.trans_prop['selectCorpus']['caption'], 
                                      directory=opath.join(self.corpusDir), 
                                      filter='*.txt')[0]

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
         self.minwordSpin.setSuffix(' %s' %self.trans_prop['minwordSpin']['suffix']['singular'])
      else:
         self.minwordSpin.setSuffix(' %s' %self.trans_prop['minwordSpin']['suffix']['plural'])

      self.maxwordSpin.setMinimum(value)
      return


   def _maximumWordsChanged(self, value, *args, **kwargs):
      '''Actions taken when the maximum number of words changed.'''

      if value == 1:
         self.maxwordSpin.setSuffix(' %s' %self.trans_prop['maxwordSpin']['suffix']['singular'])
      else:
         self.maxwordSpin.setSuffix(' %s' %self.trans_prop['maxwordSpin']['suffix']['plural'])
      
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
      centerPoint.setY(centerPoint.y())
      centerPoint.setX(centerPoint.x())
      frameGm.moveCenter(centerPoint)
      self.move(frameGm.topLeft())

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


   ############################################################
   #            Settings and rules related methods            #
   ############################################################
   
   def _setupSettings(self, *args, **kwargs):
      '''Setup the settings at startup.'''
      
      for which, values in self.rules.items():
         for setting, value in values.items():
            obj       = value['widget']
            method    = value['method']
            val       = value['value']
            
            ret       = self.setSetting(obj, method, val)
            
            if ret == -1:
               raise AttributeError('Object %s not found.' %objName)
            elif ret == -2:
               raise AttributeError('Method %s in object %s not found.' %(method, objName))
               
      # Modify rules to be correctly by methods later on (rules layout from conf file is saved in another variable)
      self._confRules = copy.deepcopy(self.rules)
      for which, values in self.rules.items():
         for setting, value in values.items():
            self.rules[which][setting] = value['value']
            
      return
   
   def saveSettings(self, *args, **kwargs):
       '''Actions taken when settings are saved.'''
       
       # Gather data necessary to save settings
       corpus      = self.corpusName
       interface   = self.currentTrans
       language    = self.languageName
       alterations = self.langAlteration
       rules       = self._confRules
       
       # Need to update the rules according to the state of each rule in self.rules dict
       for which, values in self.rules.items():
          for item, value in values.items():
             rules[which][item]['value'] = value
       
       bkd.saveConfig('configuration.yaml', corpus=corpus, interface=interface, language=language, alterations=alterations, rules=rules)
          
       # Grey out save icon
       self.saveButton.setEnabled(False)
       self.statusbar.showMessage('Saved settings')
       
       return

   def setRule(self, which=None, **kwargs):
      '''
      Set a rule with the given value. Function should be called as follows

      ... self.setRule(someRule = someValue, which='Other_rule')
      '''
      
      if which is None:
          raise ValueError('which parameter must not be None to set a rule.')
        
      for item, value in kwargs.items():
          self.rules[which][item] = value
          
      # When setting is updated we ungrey the save button
      self.saveButton.setEnabled(True)

      return
   
   def setSetting(self, objName, methodName, value):
      '''
      Set settings widget with the given value.

      :param objName: object to update
      :param methodName: method to apply to the object
      :param value: value to put into the object
      '''
      
      # Get object and method
      try:
         obj      = getattr(self, objName)
      except AttributeError:
         return -1
      
      try:
         method   = getattr(obj, methodName)
      except AttributeError:
         return -2
      
      if objName in ['rulesVow_Vow_S', 'rulesVow_Vow_A', 'rulesCon_Con_S', 'rulesCon_Con_A', 'rulesLet_Let_S', 'rules_Let_Let_A', 'rulesDel', 'rulesSwap']:
         if value:
            value = Qt.Checked
         else:
            value = Qt.Unchecked
      
      # Apply method
      method(value)
      
      return 0
      


if __name__ == '__main__':
   root   = QApplication(sys.argv)
   app    = App(root)
   sys.exit(root.exec_())
