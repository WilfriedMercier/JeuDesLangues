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
   :param dict language: dictionary describing the language used

   :param list vowels: list of vowels appearing in the sentence

   :returns: modified sentence, new vowels list, vowel removed, vowel added
   :rtype: str, list[str], str, str
   '''
   
   #print(vowels, sentence)

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

def VowtoVow_Single(sentence, language, vowels_sen=None):
   '''
   Randomly modify a vowel into another one in a randomly chosen word.

   :param str sentence: sentence to modify the vowel from
   :param dict language: dictionary describing the language used
   
   :param list vowels_sen: list of vowels appearing in the sentence

   :returns: modified sentence, picked word, new vowels list, vowel removed, vowel added
   :rtype: str, str, list[str], str, str
   '''
   
   # For debug purposes
   tmp_sen = sentence
   
   #print(vowels_sen, sentence)
   
   if vowels_sen is None:
      raise ValueError('A vowels list must be given.')
      
   # If no vowel found, do not go further
   if len(vowels_sen) == 0:
       return None, None, None, None, None
   
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
       vowels_sen.remove(vowel_out)
       
   # Add the new vowel into the vowel list if it was not already present
   if vowel_in not in vowels_sen:
      vowels_sen.append(vowel_in)

   return sentence, word, vowels_sen, vowel_out, vowel_in

def ContoCon_All(sentence, language, consonants=None):
   '''
   Randomly modify a consonant into another one in all the occurences in the sentence.

   :param str sentence: sentence to modify the consonant from
   :param dict language: dictionary describing the language used

   :param list consonants: list of consonants appearing in the sentence

   :returns: modified sentence, new consonants list, consonant removed, consonant added
   :rtype: str, list[str], str, str
   '''

   if consonants is None:
      raise ValueError('A consonants list must be given.')
      
   # If no vowel found, do not go further
   if len(consonants) == 0:
       return None, None, None, None
       
   # Pick a vowel in the sentence
   consonant_out     = random.choice(consonants)

   # Pick a vowel to put in the sentence
   consonant_in      = random.choice(language['consonants'])

   # Replace the vowel
   sentence          = sentence.replace(consonant_out, consonant_in)

   consonants.remove(consonant_out)
   if consonant_in not in consonants:
      consonants.append(consonant_in)

   # Take care of alternations
   if consonant_out in language['map_alternate_inv']:
      for alternation in language['map_alternate_inv'][consonant_out]:

         if alternation in sentence:
            sentence = sentence.replace(alternation, consonant_in)

   return sentence, consonants, consonant_out, consonant_in

def ContoCon_Single(sentence, language, consonants_sen=None):
   '''
   Randomly modify a vowel into another one in a randomly chosen word.

   :param str sentence: sentence to modify the vowel from
   :param dict language: dictionary describing the lnaguage used
   
   :param list consonants_sen: list of consonants appearing in the sentence

   :returns: modified sentence, picked word, new consonants list, consonant removed, consonant added
   :rtype: str, str, list[str], str, str
   '''
   
   if consonants_sen is None:  
      raise ValueError('A consonants list must be given.')
      
   # If no consonant found, do not go further
   if len(consonants_sen) == 0:
       return None, None, None, None, None
   
   # Split words from sentence
   words_all          = make_words(sentence)
   
   # Only keep words which have consonants
   words              = []
   consonants_list    = []
   for w in words_all:
       
       vow, con       = make_vowels_consonants(w, language)
       if len(con) != 0:
           words.append(w)
           consonants_list.append(con)
           

   ##################################
   #         Random choices         #
   ##################################

   # Pick a random word
   pos                = random.choice(range(len(words)))
   word               = words[pos]
   consonants         = consonants_list[pos]

   # Pick a consonant in the selected word
   consonant_out      = random.choice(consonants)

   # Pick a consonant to put in the sentence
   consonant_in       = random.choice(language['consonants'])


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
         sentence_rec[pos]          = sentence_rec[pos].replace(consonant_out, consonant_in)

         # Take care of alternations
         if consonant_out in language['map_alternate_inv']:
            for alternation in language['map_alternate_inv'][consonant_out]:
               if alternation in word:
                  sentence_rec[pos] = sentence_rec[pos].replace(alternation, consonant_in)

   # Reconstruct the sentence
   sentence = ' '.join(sentence_rec)

   # Remove the previous consonant from the consonant list if it disappeared from the sentence
   if consonant_out not in sentence:
       consonants_sen.remove(consonant_out)
       
   # Add the new consonant into the consonant list if it was not already present
   if consonant_in not in consonants_sen:
      consonants_sen.append(consonant_in)

   return sentence, word, consonants_sen, consonant_out, consonant_in

def LettoLet_Single():
   return

def LettoLet_All():
   return

def Swap(sentence):
   '''
   Swap two consecutive words in the sentence and return the new sentence.
   
   :param str sentence: sentence from which two words will be swapped.
   
   :returns: new sentence or None, None, None if no words could be swapped
   '''
   
   # Split the sentence excluding some characters
   sentence_split     = make_words(sentence)
   ll                 = len(sentence_split)
   ll1                = ll-1
   
   # If only a single word, we cannot swap
   if ll < 2:
      return None, None, None
   
   # Split the sentence keeping characters such as , in words
   sentence_rec       = sentence.split(' ')
   
   # Only find words ok to be swapped (no special characters)
   okPos              = []
   for pos in range(ll):
       
      # Current word to check
      split           = sentence_split[pos]
      rec             = sentence_rec[pos]
      
      # Next or previous word to check
      if pos == ll1:
         osplit       = sentence_split[pos-1]
         orec         = sentence_rec[pos-1]
      else:
         osplit       = sentence_split[pos+1]
         orec         = sentence_rec[pos+1]
         
      # We save the word only if both are ok to be swapped
      if split == rec and osplit == orec:
         okPos.append(pos)
   
   # If no words meet the criteria, no swap
   if len(okPos) == 0:
      return None, None, None
   
   # Pick a position in the sentence
   pos1               = random.choice(okPos)
   word1              = sentence_rec[pos1]
   
   if pos1 == ll1:
      pos2            = pos1-1
   else:
      pos2            = pos1+1
   
   # Replace words in sentence list
   word2              = sentence_rec[pos2]
   sentence_rec[pos2] = word1
   sentence_rec[pos1] = word2
   
   # Reconstruct the sentence
   sentence           = ' '.join(sentence_rec)
   
   return sentence, word1, word2





