import nltk
import os
import re


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
        txt = list(filter(None, txt))
        self.txt = txt

        # Only grab complete sentences
        regex = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)

        sentences = [x for x in txt if regex.search(x)]
        all_sentences = []

        # Pattern for splitting sentences
        sentence_regex = "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        for sentence in sentences:
            # Remove anything in between parenthesis, slashs, brackets,...
            sentence = removeParentheses(sentence)
            all_sentences += re.split(sentence_regex, sentence)

        self.sentences = all_sentences

        tokens = []
        tagged_sentences = []

        for sentence in self.sentences:
            # Get rid of punctuation
            # tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
            # token = tokenizer.tokenize(sentence)
            token = nltk.word_tokenize(sentence)
            tokens.append(token)
            ne_tree = nltk.chunk.ne_chunk(nltk.pos_tag(token))
            iob_tagged = nltk.chunk.tree2conlltags(ne_tree)
            tagged_sentences.append(iob_tagged)

        self.tagged_sentences = tagged_sentences
        self.tokens = tokens

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

# txt = NER("set1/a1.txt")
# s = 10
# txt.printSentence(s)
# txt.printTag(s)
# txt.basicWho(s)
# txt.basicWhat(s)
# txt.basicLocation(s)
