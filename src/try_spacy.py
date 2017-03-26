from __future__ import unicode_literals

import spacy
from spacy.en import English
parser = English()

multiSentence = "Aquarius is a constellation of the zodiac, situated between Capricornus and Pisces." \
        "Aquarius is one of the oldest of the recognized constellations along the zodiac" \
        " It was one of the 48 constellations listed by the 2nd century astronomer Ptolemy, and it remains one of the 88 modern constellations."
        

parsedData = parser(multiSentence)
sents = []

for span in parsedData.sents:
    sent = ''.join(parsedData[i].string for i in range(span.start, span.end)).strip()
    sents.append(sent)

for sentence in sents:
    print(sentence)

for span in parsedData.sents:
    sent = [parsedData[i] for i in range(span.start,span.end)]
    break

# POS tagging
for token in sent:
    print(token.orth_, token.pos_)

# dependencies
for token in parsedData:
    print(token.orth_, token.dep_, token.head.orth_, [t.orth_ for t in token.lefts], [t.orth_ for t in token.rights])

# NER
example = "The symbol of the scales is based on the Scales of Justice held by Themis, the Greek personification of divine law and custom."
parsedEx = parser(example)

# if you just want the entities and nothing else, you can do access the parsed examples "ents" property like this:
ents = list(parsedEx.ents)
print("entities!")
for entity in ents:
    print(entity.label, entity.label_, ' '.join(t.orth_ for t in entity))

