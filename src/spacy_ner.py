import spacy
from spacy.tokens.span import Span
from nltk.parse.stanford import StanfordParser
import os
import re
import sys
import string
from collections import Counter
import language_check
import grammar_check

reload(sys)
sys.setdefaultencoding('utf8')

tool = grammar_check.LanguageTool('en-US')

textFile = sys.argv[1]
qNum = int(sys.argv[2])

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

def format_question(question):
    matches = tool.check(unicode(question))
    return grammar_check.correct(unicode(question), matches)

def gscore(question):
    return float(-len(tool.check(unicode(question))))

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
        when = []

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

            # What questions
            if (sent.root.lemma_ == "be"):
                for r in sent.root.rights:
                    join = ' '.join(w.text for w in r.subtree)
                    if join[-1] == ",":
                        join = join[:-2]
                    what_question_1 = "What " + sent.root.text + " " + join + "?"
                    questions.append((format_question(what_question_1), rel+gscore(what_question_1)))
                    break
                for r in sent.root.lefts:
                    join = ' '.join(w.text for w in r.subtree)
                    if join[-1] == ",":
                        join = join[:-2]
                    what_question_2 = "What " + sent.root.text + " " + join + "?"
                    questions.append((format_question(what_question_2), rel+gscore(what_question_2)))

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
                        # print "Who " + end.text + "?"
                        who_question = "Who " + end.text + "?"
                        questions.append((format_question(who_question), rel+gscore(who_question)))
                    else:
                        # print start.text + " who " + end.text + "?"
                        who_question = start.text + " who " + end.text + "?"
                        questions.append((format_question(who_question), rel+gscore(who_question)))
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
                            final = final + token.orth_ + " "
                    # print final[:-1] + "?"
                    when_question_1 = final[:-1] + "?"
                    questions.append((when_question_1, rel+gscore(when_question_1)))
                    when.append((when_question_1, rel+gscore(when_question_1)))
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
                        # print final[:-1] + "?"
                        when_question_2 = final[:-1] + "?"
                        questions.append((when_question_2, rel+gscore(when_question_2)))
                        when.append((when_question_2, rel+gscore(when_question_2)))
                    break

            # Where questions
            for i in range(0, len(sent)-1):
                # if (sent[i].ent_type_ == "GPE" and sent[i-1].ent_type_ != "GPE"):
                if (sent[i].ent_type_ == "GPE" and sent[i-1].ent_type_ != "GPE" and sent[i-1].tag_ == "IN"):
                    # print sent
                    oneloc = str(sent[i])
                    j = i
                    while j < len(sent)-1 and sent[j+1].ent_type_ == "GPE":
                        oneloc += " " + str(sent[j+1])
                        j = j + 1
                    # possible_locations.append(oneloc)
                    i = j

                    for r in sent.root.rights:
                        if sent.root.lemma_ == "be":
                            final = "Where was "
                        elif sent.root.tag_ == "VB":
                            final = "Where do "
                        elif sent.root.tag_ == "VBP":
                            final = "Where have "
                        else:
                            final = "Where did "
                        subject = ''
                        for l in sent.root.lefts:
                            if l.right_edge.dep_=='nsubj':
                                subject = str(l.right_edge)
                                break
                            else:
                                subject =  ' '.join(w.text for w in l.subtree)
                        final += subject + " " + sent.root.lemma_ + " " + ' '.join(w.text for w  in r.subtree) + "?"
                        break
                    final = final.replace(oneloc, "")
                    where_question = final[:-1] + "?"
                    questions.append((where_question, rel+gscore(where_question)))
                    # print ""
                    break

        # DO/ DID DOES HAVE questions
            if (sent.root.pos_ == "VERB"):
                # print sent.root.tag_
                v_question = ""
                for r in sent.root.rights:

                    if sent.root.tag_ == 'VB':
                        v_question = 'Do'
                    elif sent.root.tag_ == 'VBD':
                        v_question = 'Did'
                    elif sent.root.tag_ == 'VBZ':
                        v_question = 'Does'
                    elif sent.root.tag_ == 'VBP':
                        v_question = 'Have'
                    elif sent.root.tag_ == 'VBN':
                        break
                    else:
                        break

                    subject =''
                    for l in sent.root.lefts:
                        if l.right_edge.dep_=='nsubj':
                            subject = str(l.right_edge)
                            break
                        elif v_question == 'Have':
                            subject =  ' '.join(w.text for w in l.subtree)
                            break
                        else:  subject =  ' '.join(w.text for w in l.subtree)
                    v_question += " " + subject + " " + sent.root.lemma_ + " " +' '.join(w.text for w in r.subtree) + '?'
                    break

                # print v_question
                questions.append((v_question, rel+gscore(v_question)))
                # print ""

        # Is Was Were Questions
            if (sent.root.lemma_ == "be"):
                for r in sent.root.rights:
                    if sent.root.text == '\'s':
                        isquest1 == 'Is'
                    else:
                        isquest1 = sent.root.text.capitalize()
                    for l in sent.root.lefts:
                        isquest1 += " " + ' '.join(w.text for w in l.subtree)
                    isquest1 += ' ' +' '.join(w.text for w in r.subtree) +'?'
                    break
                # print isquest1
                questions.append((isquest1, rel+gscore(isquest1)))
                # print ""

        questions = sorted(questions, key=lambda x: x[1], reverse=True)
        goodQuestions = []
        for q in questions:
            if q[0].count(' ') > 3:
                sentence = q[0]
                matches = tool.check(sentence)
                if len(matches) == 0:
                    goodQuestions.append(q[0])

        for i in range(0, qNum):
            if (i*4) < len(goodQuestions)
                print goodQuestions[i*4]


txt = NER(textFile)
