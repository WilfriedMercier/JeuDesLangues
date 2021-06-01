import nltk
import random


##################################################
#         Extracting words and sentences         #
##################################################

def make_sentences(files):
   '''
   Extract sentences out of a corpus of text files.

   :param files: file or list of files from which the sentences are extracted
   :type files: str or list[str]

   :returns: list of sentences
   :rtype: list[str]
   '''

   if isinstance(files, str):
      files = [files]

   sentences        = []
   for file in files:
      with open(file, 'r') as f:
         text       = f.read()
         text       = text.replace('-\n', '')
         text       = text.replace('\n', ' ')
         stcs       = nltk.sent_tokenize(text)
         sentences += stcs

   return sentences


def make_words(sentence, exclude=[',', '.', ';', ':', '!', '?', '--', '(', ')']):
   '''
   Extract words from sentences, removing the following characters: ,;.:!--?

   :param str sentence: sentence to extract words from

   :param list[str] exclude: (**Optional**) characters to not consider as words and to exclude from the words list

   :returns: list of words
   :rtype: list[str]
   '''

   words = nltk.word_tokenize(sentence)
   words = [i for i in words if i not in exclude]

   return words


def pick_sentence(sentences, minWords=1, maxWords=14, maxPass=100):
   '''
   Pick a sentence in a list of sentences with correct properties.

   :param list[str] sentences: list of sentences to pick a sentence from

   :param int maxPass: (**Optional**) maximum number of passes allowed when picking up a sentence
   :param int maxWords: (**Optional**) maximum number of words allowed in the sentence
   :param int minWords: (**Optional**) minimum number of words allowed in the sentence

   :returns:

      * if **npass** < **maxPass** : picked sentence, list of words and number of words
      * else : None, [], 0

   :rtype:

      * **npass** < **maxPass** : str, list[str], int
      * else : None, list, int
   '''

   lwords      = maxWords+1 # Number of words in the picked sentence
   npass       = 0          # Number of passes when picking up a sentence

   # Loop until we find a sentence which matches user preferences
   sentence    = None
   while (lwords < minWords or lwords > maxWords) and npass < maxPass:

      # Pick just one
      sentence = random.choice(sentences)

      # Count number of words
      words    = make_words(sentence)
      lwords   = len(words)
      npass   += 1

   if npass < maxPass:
      return sentence, words, lwords
   else:
      return None


#################################
#        Modify sentences       #
#################################

# nltk.tokenize.legality_principle module to split into syllables

def VowtoVow_All(sentence):
   







# Split text into sentences
files                   = ['../corpus/corpus_balzac.txt']
sentences               = make_sentences(files)
sentence, words, lwords = pick_sentence(sentences, minWords=3, maxWords=10, maxPass=100)

print(sentence)
print(lwords, words)

