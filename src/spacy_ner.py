import spacy
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

        #txt = filter(lambda x : any (p in x for p in punct), txt)

        txt = [x.strip() for x in txt]

        sentence_regex = "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        regex = re.compile(sentence_regex)

        txt = [x for x in txt if regex.search(x)]
        txt = ''.join(str(elem) for elem in txt)
        self.txt = txt
        nlp = spacy.load('en')
        doc = nlp(unicode(txt))
        
        for sent in doc.sents:
            print sent.string

    def basicWho(self, i):
        tagged = self.tagged_sentences[i]
        people = []
        person = ""
        for word in tagged:
            if word[2] == "B-PERSON":
                if person != "":
                    people.append(person)
                person = word[0]
            elif word[2] == "I-PERSON":
                person += " " + word[0]
            elif person != "":
                people.append(person)
                person = ""
        if person != "":
            people.append(person)
        for person in people:
            print("Who is " + person + "?")

    def basicLocation(self, i):
        tagged = self.tagged_sentences[i]
        places = []
        place = ""
        for word in tagged:
            if word[2] == "B-GPE":
                place = word[0]
            elif word[2] == "I-GPE":
                place += " " + word[0]
            elif place != "":
                places.append(place)
                place = ""
        if place != "":
            places.append(place)
        for place in places:
            print("What happened in " + place + "?")

    def basicWhat(self, i):
        tagged = self.tagged_sentences[i]
        orgs = []
        org = ""
        for word in tagged:
            if word[2] == "B-ORGANIZATION":
                print(word)
                org = word[0]
            elif word[2] == "I-ORGANIZATION":
                org += " " + word[0]
                print(org)
            elif org != "":
                orgs.append(org)
                org = ""
        if org != "":
            orgs.append(org)
        for org in orgs:
            print("What is " + org + "?")

    def printSentence(self, i):
        print(self.sentences[i])

    def printTag(self, i):
        print(self.tagged_sentences[i])

    def drawTree(self, i):
        ne_tree = nltk.chunk.conlltags2tree(self.tagged_sentences[i])
        ne_tree.draw()

txt = NER("set2/a1.txt")
