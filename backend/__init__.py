# Init file for this directory
# Mercier Wilfried - IRAP

import yaml
import os.path           as     opath
from   functools         import reduce
from   glob              import glob
from   copy              import deepcopy
from   PyQt5.QtGui       import QIcon, QPixmap

# Custom imports
import backend.sentences as     sen

class LanguageGroup:
    '''A class which combines all data relative to a language group.'''
    
    def __init__(self, sentence, language, vowels, consonants, idd=None, *args, **kwargs):
        '''
        Init method for this class.
        
        :param list consonants: list of consonants in the sentence
        :param dict language: dictionary representing the considered language
        :param str sentence: main sentence which is going to be modified
        :param list vowels: list of vowels in the sentence
        
        :param str idd: (**Optional**) identifier for this language group
        '''
        
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
                            'ContoCon_Single' : self.ContoCon_Single
                           }
        
        
        
    def applyRule(self, rule, *args, **kwargs):
        ''''
        Apply a given rule to the current sentence.
        
        :param str rule: rule to apply
        
        :returns: message to output in admin mode
        :rtype: str
        '''
        
        if rule not in self.ruleMethods:
            print('No rule %s found in rules methods %s' %(rule, self.ruleMethods.keys()))
            msg = None
        else:
            msg = self.ruleMethods[rule](len(self.sentence))
            
        return msg
    
    
    ###################################
    #              Rules              #
    ###################################
    
    # Vowels
    def VowtoVow_All(self, turn, *args, **kwargs):
        ''''
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
            msg         = 'Turn %s: %s changed vowel %s to vowel %s in every word.' %(turn, self.id, vowel_out, vowel_in)
        else:
            self.sentence.append(self.sentence[-1])
            msg         = 'Turn %s: %s made no modifications because no vowel was found in the sentence.' %(turn, self.id)
        
        return msg
        
    def VowtoVow_Single(self, turn, *args, **kwargs):
        ''''
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
            msg         = 'Turn %s: %s changed vowel %s to vowel %s in word %s.' %(turn, self.id, vowel_out, vowel_in, word)
        else:
            self.sentence.append(self.sentence[-1])
            msg         = 'Turn %s: %s made no modifications because no vowel was found in sentence.' %(turn, self.id)
            
        return msg
    
    # Consonants
    def ContoCon_All(self, turn, *args, **kwargs):
        ''''
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
            msg         = 'Turn %s: %s changed consonant %s to consonant %s in every word.' %(turn, self.id, consonant_out, consonant_in)
        else:
            self.sentence.append(self.sentence[-1])
            msg         = 'Turn %s: %s made no modifications because no consonant was found in the sentence.' %(turn, self.id)
        
        return msg
        
    def ContoCon_Single(self, turn, *args, **kwargs):
        ''''
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
            msg             = 'Turn %s: %s changed consonant %s to consonant %s in word %s.' %(turn, self.id, consonant_out, consonant_in, word)
        else:
            self.sentence.append(self.sentence[-1])
            msg             = 'Turn %s: %s made no modifications because no consonant was found in sentence.' %(turn, self.id)
            
        return msg



def loadCorpus(scriptPath, corpusFile):
   '''
   Load a corpus file.

   :param str scriptPath: path where the main program is located
   :param str corpusFile: name of the corpus ascii file

   :returns: corpus text, ok flag and error message if any
   :rtype: str, boolean, str
   '''

   path       = opath.join(scriptPath, 'corpus')
   file       = opath.join(path, corpusFile)

   if not opath.isfile(file):
      return '', False, 'No corpus file %s found in %s directory.' %(corpusFile, path)
   else:
      with open(file, 'r') as f:
         text = f.read()
         return text, True, ''

def loadIcons(scriptPath, formats=['xbm', 'xpm', 'png', 'bmp', 'gif', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm']):
   '''
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
      msg           = 'Icons path %s could not be found.' %path

   return conf, ok, msg

def loadLanguage(scriptPath, languageFile, alt=True):
   '''
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
               print('Alterations %s of letter %s could not be broadcast to neither consonants, nor vowels.' %(alterations, letter))

      conf.pop('alterations')
      ok      = True
      msg     = ''
   else:
      conf    = {}
      ok      = False
      msg     = 'Language file %s could not be found.' %file

   return conf, ok, msg

def loadTranslation(scriptPath, transFile, transPath='translations'):
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
        msg                = 'Translation file %s could not be fonud.' %file
    
    return conf, ok, msg
 
def saveConfig(file, corpus=None, interface=None, language=None, alterations=None, rules=None):
   '''Save settings into configuration file.'''
   
   if None in [corpus, interface, language, alterations, rules]:
      raise ValueError('One of the variables in saveConfig is None.')
   
   # Build out dict and yaml string
   out_d = {'corpus'              : corpus,
            'interfaceLanguage'   : interface + '.yaml',
            'language'            : language,
            'languageAlterations' : alterations,
            'rules'               : rules
           }
   
   out   = yaml.dump(out_d, Dumper=yaml.Dumper)
   
   with open(file, 'w') as f:
      f.write(out)
   
   return

def setupTranslation(file):
    '''Utility function to easily change translation. See loadTranslation.'''
    
    with open(file, 'r') as f:
        trans = yaml.load(f, Loader=yaml.Loader)
    
    return trans


###################################
#          INITIAL SETUP          #
###################################

def setup(scriptPath, configFile):
   '''
   Setup program at startup.

   :param str scriptPath: path where the main program is located
   :param str configFile: name of the config file
   :returns: conf dictionary, True if everything is ok or False otherwise, error message if any
   :rtype: dict, bool, str
   '''

   file                         = opath.join(scriptPath, configFile)

   if not opath.isfile(file):
      return {}, False, 'Configuration file is missing.'
   else:
      with open(file, 'r') as f:
         conf                   = yaml.load(f, Loader=yaml.Loader)

      # Generate icons
      icons, ok, msg            = loadIcons(scriptPath)

      if not ok:
         return {}, ok, msg

      conf['icons']             = icons

      # Load default corpus file if not empty
      corpusFile                = conf['corpus']
      text, ok, msg             = loadCorpus(scriptPath, corpusFile)

      if not ok:
         return {}, ok, msg

      conf['corpusText']        = text

      # Build default language dict
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

      # Load translation file
      translation, ok, msg      = loadTranslation(scriptPath, conf['interfaceLanguage'])

      if not ok:
         return {}, ok, msg

      conf['translations']      = translation['translations']
      conf['trans_prop']        = translation['trans_prop']
      conf['trans_name']        = translation['trans_name']
      conf.pop('interfaceLanguage')

      return conf, ok, msg
