import spacy
from spacy.tokens.span import Span
import os
import re
import sys
import string
from collections import Counter

reload(sys)
sys.setdefaultencoding('utf8')
def removeParentheses(sentence):
    pCounter = 0
    newSentence = ""
    for i in range(len(sentence)):
        if (sentence[i] == '(' or sentence[i] == '{'):
            pCounter += 1
        if (sentence[i] == ')' or sentence[i] == '}'):
            pCounter -= 1
        if (not(sentence[i] == '(' or sentence[i] == '{' or
                sentence[i] == ')' or sentence[i] == '}') and pCounter == 0):
            newSentence += sentence[i]
    # Remove anything in slashes
    newSentence = re.sub('\/([^\)]+)\/', '', newSentence)
    return newSentence


class NER(object):

    def __init__(self, txt_path):
        super(NER, self).__init__()

        cur_path = os.path.dirname(__file__)
        rel_path = '../data/' + txt_path
        f_path = os.path.join(cur_path, rel_path)


        with open(f_path, 'r') as f:
            txt = f.readlines()

        txt = [x.strip() for x in txt]

        sentence_regex = "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        regex = re.compile(sentence_regex)

        txt = [x for x in txt if regex.search(x)]
        txt = ''.join(str(elem) for elem in txt)
        self.txt = txt
        nlp = spacy.load('en')
        doc = nlp(unicode(txt))

        questions = []
        who = []

        words = []
        for word in doc:
            if word.pos_ == "NOUN" or word.pos_ == "VERB":
                words.append(word.lemma_)

        count = Counter(words)
        
        for sent in doc.sents:

            rel = 0
            for word in sent:
                rel += count.get(word.lemma_, 0)

            rel = rel/float(len(sent))

            if (sent.root.lemma_ == "be"):
                for r in sent.root.rights:
                    join = ' '.join(w.text for w in r.subtree)
                    if join[-1] == ",":
                        join = join[:-2]
                    questions.append(("What " + sent.root.text + " " + join + "?", rel))
                    break
                for r in sent.root.lefts:
                    join = ' '.join(w.text for w in r.subtree)
                    if join[-1] == ",":
                        join = join[:-2]
                    questions.append(("What " + sent.root.text + " " + join + "?", rel))

            # Who questions
            subject = ["he", "she"]
            for i in range(0, len(sent)-1) :
                if sent[i].dep_ == "nsubj" and sent[i].ent_type_ == "PERSON" or sent[i].text in subject:
                    if i > 0:
                        start = Span(doc, sent.start, i+sent.start-1)
                    else:
                        start = Span(doc, sent.start, sent.start)
                    i = i+1
                    while i < len(sent)-1:
                        if sent[i].ent_type_ == "PERSON":
                            i = i+1
                        elif sent[i].dep_ == "nsubj":
                            i = i+1
                        else:
                            break
                    end = Span(doc, i + sent.start, sent.end-1)
                    if (len(start) == 0):
                        print "Who " + end.text + "?"
                        questions.append(("Who " + end.text + "?", rel))
                        who.append("Who " + end.text + "?")
                    else:
                        print start.text + " who " + end.text + "?"
                        questions.append((start.text + " who " + end.text + "?", rel))
                        who.append(start.text + " who " + end.text + "?")
                        questions.append(("Who " + end.text + "?", rel))
                    break

            # When questions
            # Only works when original sentence is "In ____, blah blah."
            for i in range(0, len(sent)-1):
                if (sent[i].ent_type_ == "DATE" and sent[i].pos_ != "ADJ"): 
                    hi = Span(doc, sent.start, i+sent.start)
                    head = sent[i].head
                    while i < len(sent) - 1 and (sent[i].ent_type_ == "DATE" or sent[i].pos_ == "PUNCT"):
                        i = i+1
                    end = Span(doc, i + sent.start, sent.end-1)
                    verb = sent[i]
                    for t in sent.root.lefts:
                        verb = t
                    if verb.lemma_ == "be":
                        final = "When was "
                    else:
                        final = "When did "
                    for token in end:
                        if verb.lemma_ == "be" and token.lemma_ == "be":
                            final = final
                        elif verb.lemma_ != "be" and token == sent.root:
                            final = final + sent.root.lemma_ + " "
                        else:
                            if token.ent_type_ == "":
                                final = final + token.lower_ + " "
                            else:
                                final = final + token.text + " "
                    print final[:-1] + "?"
                    questions.append((final[:-1] + "?", rel))
                    break

            for i in range(0, len(sent)-1):
                if (sent[i].ent_type_ == "DATE"): 
                    if (i > 0):
                        front = Span(doc, sent.start, i+sent.start-1)
                    else:
                        font = []
                    valid = False
                    while i < len(sent) - 1 and (sent[i].ent_type_ == "DATE" or sent[i].pos_ == "PUNCT"):
                        i = i+1
                        valid = True
                    if valid:
                        end = Span(doc, sent.start + i, sent.end-1)
                        verb = sent[i]
                        for t in sent.root.lefts:
                            verb = t
                        if verb.lemma_ == "be":
                            final = "When was "
                        else:
                            final = "When did "
                        for token in front:
                            if token.ent_type_ == "":
                                final = final + token.lower_ + " "
                            else:
                                final = final + token.text + " "
                        for token in end:
                            if verb.lemma_ == "be" and token.lemma_ == "be":
                                final = final
                            elif verb.lemma_ != "be" and token == sent.root:
                                final = final + sent.root.lemma_ + " "
                            else:
                                final = final + token.orth_ + " "
                        print final[:-1] + "?"
                        questions.append((final[:-1] + "?", rel))
                    break

        for i in range(0, 10):
            print ""


        questions = sorted(questions, key=lambda x: x[1], reverse=True)
        for q in questions:
            if q[0].count(' ') > 3 and q[0].count(' ') < 20:
                print q[0]
                print q[1]

        for i in range(0, 10):
            print ""

        for q in who:
            print q

txt = NER("set4/a4.txt")
