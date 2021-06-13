import nltk
import random


#################################################################################
#         Extracting sentences, words, consonants, vowels and syllables         #
#################################################################################

def make_sentences(texts):
   '''
   Extract sentences out of a corpus of texts.

   :param texts: text or list of texts from which the sentences are extracted
   :type texts: str or list[str]

   :returns: list of sentences
   :rtype: list[str]
   '''

   if isinstance(texts, str):
      texts         = [texts]

   sentences        = []
   for text in texts:
         text       = text.replace('-\n', '')
         text       = text.replace('\n', ' ')
         stcs       = nltk.sent_tokenize(text)
         sentences += stcs

   return sentences


def make_words(sentence, exclude=[',', '.', ';', ':', '!', '?', '--', '(', ')', '"', '»', '«']):
   '''
   Extract words from sentences, removing some characters.

   :param str sentence: sentence to extract words from

   :param list[str] exclude: (**Optional**) characters to not consider as words and to exclude from the words list. If None, these characters are not removed.

   :returns: list of words
   :rtype: list[str]
   '''

   words = nltk.word_tokenize(sentence)

   if exclude is not None:
      words = [i for i in words if i not in exclude]

   return words

def make_vowels_consonants(sentence, language):
   '''
   Extract all the vowels and consonants in a given sentence.

   :param str sentence: sentence to extract vowels and consonants from
   :param dict language: dictionary defining the alphabet of the language used to extract vowels and consonants from the sentence

   :returns: list of vowels, list of consonants
   :rtype: list[str], list[str]
   '''

   # If alternations are considered, then they are similar to the characters they map to, in which case they do not appear in the vowel or consonant lists but must be mapped
   # If alternations are not considered, alteradted characters are different and therefore do appear in the vowel and consonant lists
   alternations = language['map_alternate']

   consonants   = []
   vowels       = []

   for char in sentence:

      if char in language['consonants'] and char not in consonants:
         consonants.append(char)
      elif char in language['vowels'] and char not in vowels:
         vowels.append(char)
      else:
         # If character is neither a vowel or a consonant, it can be an alternated character
         if char in alternations.keys():
            if alternations[char] in language['vowels'] and alternations[char] not in vowels:
               vowels.append(alternations[char])
            elif alternations[char] in language['consonants'] and alternations[char] not in consonants:
               consonants.append(alternations[char])

   return vowels, consonants

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

def VowtoVow_All(sentence, language, vowels=None):
   '''
   Randomly modify a vowel into another one in all the occurences in the sentence.

   :param str sentence: sentence to modify the vowel from
   :param dict language: dictionary describing the lnaguage used

   :param list vowels: list of vowels appearing in the sentence

   :returns: modified sentence, new vowels list, vowel removed, vowel added
   :rtype: str, list[str], str, str
   '''

   if vowels is None:
      raise ValueError('A vowels list must be given.')
      
   # If no vowel found, do not go further
   if len(vowels) == 0:
       return None, None, None, None
       
   # Pick a vowel in the sentence
   vowel_out         = random.choice(vowels)

   # Pick a vowel to put in the sentence
   vowel_in          = random.choice(language['vowels'])

   # Replace the vowel
   sentence          = sentence.replace(vowel_out, vowel_in)

   vowels.remove(vowel_out)
   if vowel_in not in vowels:
      vowels.append(vowel_in)

   # Take care of alternations
   if vowel_out in language['map_alternate_inv']:
      for alternation in language['map_alternate_inv'][vowel_out]:

         if alternation in sentence:
            sentence = sentence.replace(alternation, vowel_in)

   return sentence, vowels, vowel_out, vowel_in

def VowtoVow_Single(sentence, language):
   '''
   Randomly modify a vowel into another one in a randomly chosen word.

   :param str sentence: sentence to modify the vowel from
   :param dict language: dictionary describing the lnaguage used

   :returns: modified sentence, picked word, new vowels list, vowel removed, vowel added
   :rtype: str, str, list[str], str, str
   '''
   
   # Split words from sentence
   words_all          = make_words(sentence)
   
   # Only keep words which have vowels
   words              = []
   vowels_list        = []
   for w in words_all:
       
       vow, con       = make_vowels_consonants(w, language)
       if len(vow) != 0:
           words.append(w)
           vowels_list.append(vow)
           
   # If no vowel found, do not go further
   if len(words) == 0:
       return None, None, None, None, None

   ##################################
   #         Random choices         #
   ##################################

   # Pick a random word
   pos                = random.choice(range(len(words)))
   word               = words[pos]
   vowels             = vowels_list[pos]

   # Pick a vowel in the selected word
   vowel_out          = random.choice(vowels)

   # Pick a vowel to put in the sentence
   vowel_in           = random.choice(language['vowels'])


   ############################
   #      Split sentence      #
   ############################

   # Split the sentence excluding some characters
   sentence_split     = make_words(sentence)

   # Split the sentence keeping characters such as , in words
   sentence_rec       = sentence.split(' ')


   ###########################################
   #            Replace the vowel            #
   ###########################################

   for pos in range(len(sentence_split)):
      if sentence_split[pos].lower() == word.lower():
         sentence_rec[pos]          = sentence_rec[pos].replace(vowel_out, vowel_in)

         # Take care of alternations
         if vowel_out in language['map_alternate_inv']:
            for alternation in language['map_alternate_inv'][vowel_out]:
               if alternation in word:
                  sentence_rec[pos] = sentence_rec[pos].replace(alternation, vowel_in)

   # Reconstruct the sentence
   sentence = ' '.join(sentence_rec)

   # Remove the previous vowel from the vowel list if it disappeared from the sentence
   if vowel_out not in sentence:
       vowels.remove(vowel_out)
       
   # Add the new vowel into the vowel list if it was not already present
   if vowel_in not in vowels:
      vowels.append(vowel_in)

   return sentence, word, vowels, vowel_out, vowel_in

