import spacy
from spacy.tokens.span import Span
import os
import re
import sys  
import string

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


        punct = {'.!?'}
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
        
        for sent in doc.sents:
            if (sent.root.lemma_ == "be"):
                print sent
                for r in sent.root.rights:
                    print "What " + sent.root.text + " " + ' '.join(w.text for w in r.subtree) + "?"
                    break
                right = ""
                for r in sent.root.lefts:
                    right = "What " + sent.root.text + " " + ' '.join(w.text for w in r.subtree) + "?"
                print right
                print " "

        for sent in doc.sents:
            for i in range(0, len(sent)-1) :
                if sent[i].dep_ == "nsubj" and sent[i].ent_type_ == "PERSON" or sent[i].text in subject:
                    print sent
                    hi = Span(doc, sent.start, i+sent.start)
                    i = i+1
                    while i < len(sent)-1:
                        if sent[i].ent_type_ == "PERSON":
                            i = i+1
                        elif sent[i].dep_ == "nsubj":
                            i = i+1
                        else:
                            break
                    end = Span(doc, i + sent.start, sent.end-1)
                    if (hi.text == ""):
                        print "Who " + end.text + "?"
                    else:
                        print hi.text + " who " + end.text + "?"
                    print ""
                    break
txt = NER("set1/a1.txt")
