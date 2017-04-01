import os
import re
import sys
import spacy

reload(sys)
sys.setdefaultencoding('utf8')
from collections import Counter

#prints the most common nouns in article
with open("../data/set1/a.txt", 'r') as f:
    txt = f.readlines()

txt = [x.strip() for x in txt]
nlp = spacy.load('en')
doc = nlp(unicode(txt))

words = []

for word in doc:
    if word.pos_ == "NOUN":
        words.append(word.lower_)

print Counter(words).most_common(100)

