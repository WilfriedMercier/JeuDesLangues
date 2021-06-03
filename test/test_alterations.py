import sentences  as     st
import os.path    as     opath
import yaml

def loadLanguage(scriptPath, languagePath, languageFile, alt=True):
   '''
   Load and setup language properties.

   :param str scriptPath: path where the main program is located
   :param str languagePath: path where the language file is located **relative to scriptPath**
   :param str languageFile: language configuration file. It must be of YAML type.

   :param bool alt: (**Optional**) whether to consider alterate forms as independent letters or not

   :returns: language dictionary defining vowels and consonants, ok flag and error message
   :rtype: dict, bool, str
   '''

   file       = opath.join(scriptPath, languagePath, languageFile)

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
      ok      = False
      msg     = 'Language file %s could not be found.' %file

   return conf, ok, msg

# Single sentence corpus as test example
corpus = "Nous fûmes entourées d'une étrange lueur rougeâtre, et à la vielle du départ, nous partîmes."

# Generate language dict:
#   - alt = True consider that alternations (e.g. à for a) are similar as their parent form
#   - alt = False consider that alternations are different vowels or consonants

language, ok, msg = loadLanguage('../', 'backend/languages', 'French.yaml', alt=True)

#print('Language:\n', language)

# Show word separation
sentence, words, lwords = st.pick_sentence([corpus], minWords=3, maxWords=100, maxPass=100)
print('Sentence  :', sentence)
print('Split     :', lwords, words)

# Show vowels and consonants separation
vowels, consonants = st.make_vowels_consonants(sentence.lower(), language)
print('Vowels    :', vowels)
print('Consonants:', consonants)

# Show vowel to vowel random modification in all words
sentence, vowels, vout, vin = st.VowtoVow_All(sentence, language, vowels=vowels)
print(vout, '->',  vin)
print('Sentence  :', sentence)
print('Vowels    :', vowels)

# Show vowel to vowel random modification in all words
sentence, word, vowels, vout, vin = st.VowtoVow_Single(sentence, language)
print(word, vout, '->',  vin)
print('Sentence  :', sentence)
print('Vowels    :', vowels)
