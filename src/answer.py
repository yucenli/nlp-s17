import spacy
import math
import os
import re
import sys
from collections import Counter, defaultdict

nlp = spacy.load('en')

reload(sys)
sys.setdefaultencoding('utf8')


def main():

    inputs = sys.argv[1:]
    txt_file = inputs[0]
    question_file = inputs[1]

    with open(question_file) as f:
        questionsList = f.readlines()
    questionsList = [x.strip() for x in questionsList]

    for question in questionsList:
        print(question)
        print("ANSWERS:")
        print("*" * 80)
        CosineSim(txt_file, question)
        print("*" * 80)
        print


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
        self.answers = []
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
        self.answerQuestion()

    def getRoot(self):
        sentence = nlp(unicode(self.question))
        root = [w for w in sentence if w.head is w][0]
        self.root = root.lemma_.lower()

    def answerQuestion(self):
        firstSentScore = self.sentSimCount[self.sortSentSimCount[0]]
        secSentScore = self.sentSimCount[self.sortSentSimCount[1]]
        if (firstSentScore - secSentScore > 0.1):
            print(self.sortSentSimCount[0])
            self.determineQuestion(self.sortSentSimCount[0])
        else:
            relevSentences = self.filterByRoot(self.sortSentSimCount[:10])
            for sent in relevSentences:
                print(sent)
                self.determineQuestion(sent)
        if not self.answers:
            self.answers.append(self.sortSentSimCount[0])
        self.printAnswers()
        # print('*' * 75)

    def filterByRoot(self, sentences):
        filteredSentences = []
        for sent in sentences:
            doc = nlp(unicode(sent))
            for token in doc:
                if token.lemma_.lower() == self.root:
                    filteredSentences.append(sent)
                    break
        return(filteredSentences)

    def printAnswers(self):
        # for a in self.answers[:1]:
        for a in self.answers:
            print(a)

    def determineQuestion(self, sentence):
        questionDoc = nlp(unicode(self.question))
        questionTypeFound = False
        for word in questionDoc:
            if word.text.lower() == "who":
                self.answerWho(sentence)
                questionTypeFound = True
            elif word.text.lower() == "where":
                self.answerWhere(sentence)
                questionTypeFound = True
            elif word.text.lower() == "when":
                self.answerWhen(sentence)
                questionTypeFound = True
        if not questionTypeFound:
            self.answers.append(sentence)

    def answerWho(self, sentence):
        doc = nlp(unicode(sentence))
        for ent in doc.ents:
            if (ent.label_ == "PERSON") and (ent.text not in self.question):
                self.answers.append(ent.text)

    def answerWhere(self, sentence):
        doc = nlp(unicode(sentence))
        for ent in doc.ents:
            if (ent.label_ == "GPE") and (ent.text not in self.question):
                self.answers.append(ent.text)

    def answerWhen(self, sentence):
        doc = nlp(unicode(sentence))
        for ent in doc.ents:
            if (ent.label_ in ["DATE", "TIME"]) and (ent.text not in self.question):
                self.answers.append(ent.text)


if __name__ == '__main__':
    main()
