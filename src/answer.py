import spacy
import math
import os
import re
import sys
from collections import Counter, defaultdict
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import linear_kernel

nlp = spacy.load('en')

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


def removeSemiColons(txt):
    newTxt = []
    for sentence in txt:
        if ";" in sentence:
            newSentences = sentence.split(";")
            for i in range(len(newSentences)):
                if newSentences[i][-1] != ".":
                    newSentences[i] = newSentences[i] + "."
                sentenceWords = newSentences[i].split()
                sentenceWords[0] = sentenceWords[0].capitalize()
                sentenceWords.append(" ")
                newSentences[i] = " ".join(sentenceWords)
            newTxt = newTxt + newSentences
        else:
            newTxt.append(sentence)
    return newTxt


class NER(object):

    def __init__(self, txt_path, q_root):
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
        txt = removeSemiColons(txt)
        txt = ''.join(str(elem) for elem in txt)
        self.txt = txt
        self.relevSentences = []
        doc = nlp(unicode(txt))
        for sent in doc.sents:
            # print(sent.string)
            # print("\n")
            if (sent.root.lemma_ == q_root):
                self.relevSentences.append(sent.string)
                continue

WORD = re.compile(r'\w+')


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    # words = WORD.findall(text)
    wordVector = []
    doc = nlp(unicode(text))
    for token in doc:
        wordVector.append(token.lemma_.lower())
    return Counter(wordVector)


class CosineSim(object):

    def __init__(self, txt_path, question):
        super(CosineSim, self).__init__()

        cur_path = os.path.dirname(__file__)
        rel_path = '../data/' + txt_path
        f_path = os.path.join(cur_path, rel_path)
        with open(f_path, 'r') as f:
            txt = f.readlines()

        txt = [x.strip() for x in txt]

        sentence_regex = "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        regex = re.compile(sentence_regex)

        txt = [x for x in txt if regex.search(x)]
        txt = removeSemiColons(txt)
        txt = ' '.join(str(elem) for elem in txt)
        self.txt = txt
        self.question = question
        self.getRoot()
        self.sentSimCount = defaultdict(float)
        questionVec = text_to_vector(question)
        doc = nlp(unicode(txt))
        for sent in doc.sents:
            sentVector = text_to_vector(sent.string)
            cosine = get_cosine(questionVec, sentVector)
            self.sentSimCount[sent.string] = cosine
        self.sortSentSimCount = sorted(self.sentSimCount,
                                       key=self.sentSimCount.get,
                                       reverse=True)
        self.getRelevSentences()

    def getRoot(self):
        sentence = nlp(unicode(self.question))
        root = [w for w in sentence if w.head is w][0]
        self.root = root

    def getRelevSentences(self):
        firstSentScore = self.sentSimCount[self.sortSentSimCount[0]]
        secSentScore = self.sentSimCount[self.sortSentSimCount[1]]
        if (firstSentScore - secSentScore > 0.1):
            self.answerQuestion(self.sortSentSimCount[0])
        else:
            for i in xrange(5):
                sent = self.sortSentSimCount[i]
                print(sent, self.sentSimCount[sent])
                self.answerQuestion(sent)

    def filterRelevSentences(self):
        question = nlp(unicode(self.question))
        questionRoot = [w for w in question if w.head is w][0]
        for i in xrange(5):
            answer = nlp(unicode(self.sortSentSimCount[i]))
            answerRoot = [w for w in answer if w.head is w][0]
            if answerRoot.lemma_ == questionRoot.lemma_:
                print answer.string

    def answerQuestion(self, sentence):
        questionDoc = nlp(unicode(self.question))
        for word in questionDoc:
            if word.text.lower() == "who":
                self.answerWho(sentence)

    def answerWho(self, sentence):
        doc = nlp(unicode(sentence))
        for ent in doc.ents:
            if (ent.label_ == "PERSON") and (ent.text not in self.question):
                print ent.text


class CosineSim1(object):

    def __init__(self, txt_path, question):
        super(CosineSim1, self).__init__()

        cur_path = os.path.dirname(__file__)
        rel_path = '../data/' + txt_path
        f_path = os.path.join(cur_path, rel_path)
        with open(f_path, 'r') as f:
            txt = f.readlines()

        txt = [x.strip() for x in txt]

        sentence_regex = "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        regex = re.compile(sentence_regex)

        txt = [x for x in txt if regex.search(x)]
        txt = removeSemiColons(txt)
        txt = ''.join(str(elem) for elem in txt)
        self.txt = txt
        self.sentences = []
        doc = nlp(unicode(txt))
        for sent in doc.sents:
            self.sentences.append(sent.string)
        tfidf = TfidfVectorizer().fit_transform(self.sentences)
        tfidfQ = TfidfVectorizer().fit_transform([question])
        cosine_similarities = linear_kernel(tfidfQ, tfidf).flatten()
        related_docs_indices = cosine_similarities.argsort()[-5:-1]
        for i in related_docs_indices:
            print(self.sentences[related_docs_indices[i]])


# question = "Who selected Clint Dempsey eighth overall in the 2004 MLS SuperDraft?"
# sentence = nlp(unicode(question))[2]

# print([w.text for w in sentence.lefts])
# print([w.text for w in sentence.rights])

# sentence = nlp(unicode(question))
# root = [w for w in sentence if w.head is w][0]
# print root.text.lower()
# print root.lemma_

# print question

# txt = CosineSim("set1/a1.txt", question)


# question = "Where was Dempsey born?"
# sentence = nlp(unicode(question))[2]

# print([w.text for w in sentence.lefts])
# print([w.text for w in sentence.rights])

# sentence = nlp(unicode(question))
# root = [w for w in sentence if w.head is w][0]
# print root.text.lower()
# print root.lemma_

# print question

# txt = NER("set1/a1.txt", root.lemma_)


# question = "Who composed the Slumdog Millionaire soundtrack?"
# print(question)
# sentence = nlp(unicode(question))

# for word in sentence:
#     print(word.text, word.pos_, word.dep_, word.head.text)

# root = [w for w in sentence if w.head is w][0]
# print(root.text.lower())
# print(root.lemma_)

# answer = nlp(unicode("The Slumdog Millionaire soundtrack was composed by A. R. Rahman, who planned the score for over two months and completed it in two weeks."))

# for word in answer:
#     print(word.text, word.pos_, word.dep_, word.head.text)


# if root.lemma_ != "be":
#     txt = NER("set1/a6.txt", root.lemma_)
#     for sent in txt.relevSentences:
#         print(sent)
# txt = CosineSim("set4/a3.txt", question)
# txt.filterRelevSentences()


with open("questions.txt") as f:
    questionsList = f.readlines()
questionsList = [x.strip() for x in questionsList]

for question in questionsList:
    print(question)
    sentences = CosineSim("set3/a1.txt", question)
    sentences.filterRelevSentences()
