import numpy as np

import nltk
nltk.download('punkt_tab')
from nltk.stem.snowball import FrenchStemmer

# Initialisation du stemmer pour le français
stemmer = FrenchStemmer()



def tokenize(sentence):
    
    return nltk.word_tokenize(sentence)


def stem(word):
    
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence, words):
    
   tokenized_sentence=[stem(w) for w in tokenized_sentence]
   bag=np.zeros(len(words),dtype=np.float32)
   for idx,w in enumerate(words):
       if  w in tokenized_sentence:
           bag[idx]=1.0
    
   return bag 
  
  



