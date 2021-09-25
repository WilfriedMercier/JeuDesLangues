# Init file for this directory
# Mercier Wilfried - IRAP

import yaml
import os.path           as     opath
from   functools         import reduce
from   glob              import glob
from   copy              import deepcopy
from   typing            import Union, List, Optional, Any
from   PyQt5.QtGui       import QIcon, QPixmap

# Custom imports
import backend.sentences as     sen

class LanguageGroup:
    r'''A class which combines all data relative to a language group.'''
    
    def __init__(self, sentence: str, language: dict, vowels: List[str], consonants: List[str], idd: Optional[str] = None, *args, **kwargs) -> None:
        r'''
        Init method for this class.
        
        :param str sentence: main sentence which is going to be modified
        :param dict language: dictionary representing the considered language
        :param list vowels: list of vowels in the sentence
        :param list consonants: list of consonants in the sentence
        
        :param str idd: (**Optional**) identifier for this language group
        '''
        
        #: Identifier
        self.id          = idd
        
        # Keep track of sentences each turn in a list
        self.sentence    = [sentence]
        
        # Vowels and consonants in the sentence
        self.consonants  = deepcopy(consonants)
        self.vowels      = deepcopy(vowels)
        
        # Language dict
        self.language    = deepcopy(language)
        
        # Rule methods
        self.ruleMethods = {'VowtoVow_All'    : self.VowtoVow_All,
                            'VowtoVow_Single' : self.VowtoVow_Single,
                            'ContoCon_All'    : self.ContoCon_All,
                            'ContoCon_Single' : self.ContoCon_Single,
                            'Swap'            : self.Swap
                           }
        
    def applyRule(self, rule: str, *args, **kwargs) -> str:
        r''''
        Apply a given rule to the current sentence.
        
        :param str rule: rule to apply
        
        :returns: message to output in admin mode
        :rtype: str
        '''
        
        if rule not in self.ruleMethods:
            print(f'No rule {rule} found in rules methods {self.ruleMethods.keys()}')
            msg = None
        else:
            msg = self.ruleMethods[rule](len(self.sentence))
            
        return msg
    
    
    ###################################
    #              Rules              #
    ###################################
    
    def ContoCon_All(self, turn: str, *args, **kwargs) -> str:
        r''''
        Consonant to consonant on all words rule.
        
        :param str turn: name of the turn to put in the sentence dict
        
        :returns: output message for admin mode
        :rtype: str
        '''
        
        # Transform sentence
        out                 = sen.ContoCon_All(self.sentence[-1], self.language, consonants=self.consonants)
        if None not in out:

            sentence        = out[0]
            consonants      = out[1]
            consonant_out   = out[2] 
            consonant_in    = out[3]
            
            # Update vowels
            self.consonants = consonants
            
            # Update sentence
            self.sentence.append(sentence)
            
            # Message to output for admin mode
            msg         = f'Turn {turn}: {self.id} changed consonant {consonant_out} to consonant {consonant_in} in every word.'
        else:
            self.sentence.append(self.sentence[-1])
            msg         = f'Turn {turn}: {self.id} made no modifications because no consonant was found in the sentence.'
        
        return msg
        
    def ContoCon_Single(self, turn: str, *args, **kwargs) -> str:
        r''''
        Consonant to consonant on a single word rule.
        
        :param str turn: name of the turn to put in the sentence dict
        
        :returns: output message for admin mode
        :rtype: str
        '''
        
        # Transform sentence
        out                 = sen.ContoCon_Single(self.sentence[-1], self.language, consonants_sen=self.consonants)
        if None not in out:
        
            sentence        = out[0]
            word            = out[1]
            consonants      = out[2]
            consonant_out   = out[3] 
            consonant_in    = out[4]
            
            # Update vowels
            self.consonants = consonants
            
            # Update sentence
            self.sentence.append(sentence)
        
            # Message to output for admin mode
            msg             = f'Turn {turn}: {self.id} changed consonant {consonant_out} to consonant {consonant_in} in word {word}.'
        else:
            self.sentence.append(self.sentence[-1])
            msg             = f'Turn {turn}: {self.id} made no modifications because no consonant was found in sentence.' 
            
        return msg
    
    def Swap(self, turn: str, *args, **kwargs) -> str:
        r'''
        Swap two consecutive words rule.
        
        :param str turn: name of the turn to put in the sentence dict
        
        :returns: output message for admin mode
        :rtype: str
        '''
        
        # Transform sentence
        out          = sen.Swap(self.sentence[-1])
        
        if None not in out:
            
            sentence = out[0]
            word1    = out[1]
            word2    = out[2]
            
            self.sentence.append(sentence)
            
            # Message to output for admin mode
            msg      = f'Turn {turn}: {self.id} swaped word {word1} with word {word2}.'
        else:
            self.sentence.append(self.sentence[-1])
            msg      = f'Turn {turn}: {self.id} made no modifications because no words could be swaped.'
            
        return msg
    
    def VowtoVow_All(self, turn: str, *args, **kwargs) -> str:
        r''''
        Vowel to vowel on all words rule.
        
        :param str turn: name of the turn to put in the sentence dict
        
        :returns: output message for admin mode
        :rtype: str
        '''
        
        # Transform sentence
        out             = sen.VowtoVow_All(self.sentence[-1], self.language, vowels=self.vowels)
        if None not in out:

            sentence    = out[0]
            vowels      = out[1]
            vowel_out   = out[2] 
            vowel_in    = out[3]
            
            # Update vowels
            self.vowels = vowels
            
            # Update sentence
            self.sentence.append(sentence)
            
            # Message to output for admin mode
            msg         = f'Turn {turn}: {self.id} changed vowel {vowel_out} to vowel {vowel_in} in every word.'
        else:
            self.sentence.append(self.sentence[-1])
            msg         = f'Turn {turn}: {self.id} made no modifications because no vowel was found in the sentence.'
        
        return msg
        
    def VowtoVow_Single(self, turn: str, *args, **kwargs) -> str:
        r''''
        Vowel to vowel on a single word rule.
        
        :param str turn: name of the turn to put in the sentence dict
        
        :returns: output message for admin mode
        :rtype: str
        '''
        
        # Transform sentence
        out             = sen.VowtoVow_Single(self.sentence[-1], self.language, vowels_sen=self.vowels)
        if None not in out:
        
            sentence    = out[0]
            word        = out[1]
            vowels      = out[2]
            vowel_out   = out[3] 
            vowel_in    = out[4]
            
            # Update vowels
            self.vowels = vowels
            
            # Update sentence
            self.sentence.append(sentence)
        
            # Message to output for admin mode
            msg         = f'Turn {turn}: {self.id} changed vowel {vowel_out} to vowel {vowel_in} in word {word}.'
        else:
            self.sentence.append(self.sentence[-1])
            msg         = f'Turn {turn}: {self.id} made no modifications because no vowel was found in sentence.'
            
        return msg


#######################################
#          Loading utilities          #
#######################################

def loadCorpus(scriptPath: str, corpusFile: str) -> Union[str, bool, str]:
   r'''
   Load a corpus file.

   :param str scriptPath: path where the main program is located
   :param str corpusFile: name of the corpus ascii file

   :returns: corpus text, ok flag and error message if any
   :rtype: str, boolean, str
   '''

   path       = opath.join(scriptPath, 'corpus')
   file       = opath.join(path, corpusFile)

   if not opath.isfile(file):
      return '', False, f'No corpus file {corpusFile} found in {path} directory.'
   else:
      with open(file, 'r') as f:
         text = f.read()
         
      return text, True, ''

def loadIcons(scriptPath: str, formats: List[str] = ['xbm', 'xpm', 'png', 'bmp', 'gif', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm']) -> Union[dict, bool, str]:
   r'''
   Load icons appearing in the given icon directory as QIcons objects.

   :param str scriptPath: path where the main program is located

   :returns: icons dictionary, True if everything is ok or False otherwise, error message if any
   :rtype: dict[QIcons], bool, str
   '''

   path             = opath.join(scriptPath, 'icons')
   conf             = {}

   if opath.isdir(path):
      files         = [file for file in glob(opath.join(path, '*')) if file.split('.')[-1].lower() in formats]

      for file in files:

         # Name in dict are without extension and in upper cases only
         nameList   = opath.basename(file).split('.')[:-1]
         name       = ""
         for n in nameList:
            name   += n.upper()

         conf[name] = QIcon(QPixmap(file))

      ok            = True
      msg           = ''
   else:
      ok            = False
      msg           = f'Icons path {path} not found.'

   return conf, ok, msg

def loadLanguage(scriptPath: str, languageFile: str, alt: bool = True) -> Union[dict, bool, str]:
   r'''
   Load and setup language properties.

   :param str scriptPath: path where the main program is located
   :param str languageFile: language configuration file. It must be of YAML type.

   :param bool alt: (**Optional**) whether to consider alterate forms as independent letters or not

   :returns: language dictionary defining vowels and consonants, ok flag and error message
   :rtype: dict, bool, str
   '''

   path       = opath.join(scriptPath, 'languages')
   file       = opath.join(path, languageFile)

   if opath.isfile(file):
      with open(file, 'r') as f:
         conf = yaml.load(f, Loader=yaml.Loader)

      # If we consider alternations, alternated forms must not appear in the vowel and consonant lists, but we must keep track by mapping them to their parent form
      if alt:
         conf['map_alternate']     = {}
         conf['map_alternate_inv'] = conf['alterations']

         for letter, alterations in conf['alterations'].items():
            for alteration in alterations:
               conf['map_alternate'][alteration] = letter

      # If we do not consider alternations, then alternated forms are considered as different characters and must be included into the vowel and consonant lists
      else:
         conf['map_alternate']     = {}
         conf['map_alternate_inv'] = {}

         for letter, alterations in conf['alterations'].items():
            if letter in conf['consonants']:
               conf['consonants'] += alterations
            elif letter in conf['vowels']:
               conf['vowels']     += alterations
            else:
               print(f'Alterations {alterations} of letter {letter} could not be broadcast to neither consonants, nor vowels.')

      conf.pop('alterations')
      ok      = True
      msg     = ''
   else:
      conf    = {}
      ok      = False
      msg     = f'Language file {file} not found.'

   return conf, ok, msg

def loadThemes(scriptPath: str, defaultFile: str = '', themePath: str = 'themes') -> Union[dict, bool, str]:
    r'''
    Find theme files and check that default file exists.
    
    :param str scriptPath: path where the main program is located
    
    :param str defaultFile: (**Optional**) default theme file
    :param str themePath: (**Optional**) path where the themes files are located
    
    :raises IOError: if **defaultFile** is not found in the theme directory.
    '''
    
    path    = opath.join(scriptPath, themePath)
    files   = glob(opath.join(path, '*.qss'))
    file    = opath.join(path, defaultFile)
    
    conf    = {'themes' : files, 'theme' : file}
    if opath.isfile(file) and file in files:
        ok  = True
        msg = ''
    else:
        ok  = False
        msg = f'Theme file {file} not found.'
        
    return conf, ok, msg
    

def loadTranslation(scriptPath: str, transFile: str, transPath:str = 'translations') -> Union[dict, bool, str]:
    '''
    Load and setup interface language.

    :param str scriptPath: path where the main program is located
    :param str transFile: language interface file
    :param str transPath: (**Optional**) path where the translations files are located

    :returns: translation dictionary, ok flag and error message
    :rtype: dict, bool, str
    '''
    
    path                   = opath.join(scriptPath, transPath)
    files                  = glob(opath.join(path, '*.yaml'))
    file                   = opath.join(scriptPath, transPath, transFile)
    
    conf                   = {'translations' : files}
    if opath.isfile(file):
        conf['trans_prop'] = setupTranslation(file)
        conf['trans_name'] = transFile.rsplit('.yaml')[0]
        ok                 = True
        msg                = ''
    else:
        ok                 = False
        msg                = f'Translation file {file} not found.'
    
    return conf, ok, msg
 
def saveConfig(file: str, 
               corpus:str = None, 
               interface:str = None, 
               language:str = None, 
               alterations: bool = None, 
               rules: dict = None,
               theme: str = None) -> None:
   r'''Save settings into configuration file.'''
   
   if None in [corpus, interface, language, alterations, rules, theme]:
      raise ValueError('One of the variables in saveConfig is None.')
   
   # Build out dict and yaml string
   out_d = {'corpus'              : corpus,
            'interfaceLanguage'   : interface + '.yaml',
            'language'            : language,
            'languageAlterations' : alterations,
            'theme'               : theme,
            'rules'               : rules
           }
   
   out   = yaml.dump(out_d, Dumper=yaml.Dumper)
   
   with open(file, 'w') as f:
      f.write(out)
   
   return

def setupTranslation(file: str):
    r'''Utility function to easily change translation. See loadTranslation.'''
    
    with open(file, 'r') as f:
        trans = yaml.load(f, Loader=yaml.Loader)
    
    return trans


###################################
#          INITIAL SETUP          #
###################################

def setup(scriptPath: str, configFile: str, parent: Any = None) -> Union[dict, bool, str]:
   r'''
   Setup program at startup.

   :param parent: parent widget calling this function. If None, nothing is done.
   :param str scriptPath: path where the main program is located
   :param str configFile: name of the config file
   
   :returns: conf dictionary, True if everything is ok or False otherwise, error message if any
   :rtype: dict, bool, str
   '''

   file                         = opath.join(scriptPath, configFile)

   # Splashscreen
   if parent is not None:
      parent.splashlabel.setText('Reading configuration file...')
      parent.root.processEvents()

   # Read configuration
   if not opath.isfile(file):
      return {}, False, 'Configuration file is missing.'
   else:
      with open(file, 'r') as f:
         conf                   = yaml.load(f, Loader=yaml.Loader)

      # Splashscreen
      if parent is not None:
         parent.splashlabel.setText('Loading icons...')
         parent.root.processEvents()

      ################################
      #        Generate icons        #
      ################################
      
      icons, ok, msg            = loadIcons(scriptPath)

      if not ok:
         return {}, ok, msg

      conf['icons']             = icons
      
      # Splashscreen
      if parent is not None:
         parent.splashlabel.setText('Loading corpus...')
         parent.root.processEvents()

      #################################################################
      #             Load default corpus file if not empty             #
      #################################################################
      
      corpusFile                = conf['corpus']
      text, ok, msg             = loadCorpus(scriptPath, corpusFile)

      if not ok:
         return {}, ok, msg

      conf['corpusText']        = text
      
      # Splashscreen
      if parent is not None:
         parent.splashlabel.setText('Building language...')
         parent.root.processEvents()
      
      ###################################################
      #           Build default language dict           #
      ###################################################
      
      languageFile              = conf['language']
      alterations               = conf['languageAlterations']
      language, ok, msg         = loadLanguage(scriptPath, languageFile, alt=alterations)

      if not ok:
         return {}, ok, msg

      # Add vowels and consonants into the conf dict
      conf['vowels']            = language['vowels']
      conf['consonants']        = language['consonants']
      conf['map_alternate']     = language['map_alternate']
      conf['map_alternate_inv'] = language['map_alternate_inv']
      
      # Splashscreen
      if parent is not None:
         parent.splashlabel.setText('Setup interface language...')
         parent.root.processEvents()

      ###################################################
      #              Load translation file              #
      ###################################################
      
      translation, ok, msg      = loadTranslation(scriptPath, conf['interfaceLanguage'])

      if not ok:
         return {}, ok, msg

      conf['translations']      = translation['translations']
      conf['trans_prop']        = translation['trans_prop']
      conf['trans_name']        = translation['trans_name']
      conf.pop('interfaceLanguage')
      
      ###################################
      #           Load themes           #
      ###################################
      
      themes, ok, msg           = loadThemes(scriptPath, defaultFile = conf['theme'])
      
      if not ok:
         return {}, ok, msg
     
      conf['theme']             = themes['theme']
      conf['themes']            = themes['themes']

      return conf, ok, msg
