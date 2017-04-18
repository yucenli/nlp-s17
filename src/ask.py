import spacy
from spacy.tokens.span import Span
# from nltk.parse.stanford import StanfordParser
import os
import re
import sys
# import string
from collections import Counter
# import language_check
import grammar_check

reload(sys)
sys.setdefaultencoding('utf8')
tool = grammar_check.LanguageTool('en-US')
# tool = language_check.LanguageTool('en-US')

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

def find_subject(sent):
    np_lab1 = ['nsubj', 'nsubjpass']
    np_lab2 = ['dobj', 'iobj', 'pobj']
    subject = ""
    for i in range(0, len(sent)-1):
        if sent[i].dep_ == 'nsubj' and sent[i].head.dep_ == "ROOT":
            subject = sent[i].orth_
            if sent[i].pos_ == "PRON":
                subject = subject.lower()
            break
        elif sent[i].dep_ == 'nsubjpass' and sent[i].head.dep_ == "ROOT":
            subject = sent[i].orth_
            if sent[i].pos_ == "PRON":
                subject = subject.lower()
            break
        elif sent[i].dep_ in np_lab1:
            subject = sent[i].orth_
            if sent[i].pos_ == "PRON":
                subject = subject.lower()
            break
        elif sent[i].dep_ in np_lab2:
            subject = sent[i].orth_
            if sent[i].pos_ == "PRON":
                subject = subject.lower()
            break
    if subject == "":
        subject = "UNKNOWN"
    return subject

def format_question(question):
    matches = tool.check(unicode(question))
    return grammar_check.correct(unicode(question), matches)

def two_verbs(i, sent, doc):
    if (i > 0):
        front = Span(doc, sent.start, i+sent.start-1)
    else:
        font = []
    end = Span(doc, sent.start+i+1, sent.end-1)
    quest1 = ""
    quest2 = ""

    if sent[i-1].tag_ == "VBZ" and sent[i].tag_ == "VBN" and sent[i-1].lemma_ != "be"  :
        quest1 = sent[i-1].orth_ + " " + find_subject(sent) + " "+ sent[i].orth_
        quest2 = sent[i-1].orth_ + " " + str(front) + " "+ sent[i].orth_

    elif sent[i-1].tag_ == "VBD" and sent[i].tag_ == "VBN" and sent[i-1].lemma_ == "be":
        quest1 = sent[i-1].orth_ + " " + find_subject(sent) + " " + sent[i].orth_
        quest2 = sent[i-1].orth_ + " " + str(front) + " " + sent[i].orth_

    elif sent[i-1].tag_ == "VBZ" and sent[i].tag_ == "VBN" and sent[i-1].lemma_ == "be":
        quest1 = "was" + " " + find_subject(sent) + " " + sent[i].orth_
        quest2 = "was" + " " + str(front) + " " + sent[i].orth_

    elif sent[i-1].tag_ == "MD" and sent[i].tag_ == "VB":
        quest1 = sent[i-1].orth_ + " " + find_subject(sent) + " " + sent[i].lemma_
        quest2 = sent[i-1].orth_ + " " + str(front) + " " + sent[i].lemma_

    quest1 += " " +str(end) + " ?"
    quest2 += " " +str(end) + " ?"
    return quest1, quest2

def one_verb(i, sent, doc):
    if (i > 0):
        front = Span(doc, sent.start, i+sent.start)
    else:
        font = []
    end = Span(doc, sent.start+i+1, sent.end-1)
    quest1 = ""
    quest2 = ""

    if sent[i].tag_ == "VBD" and sent[i].lemma_ != "be":
        quest1 = "did"+ " " + find_subject(sent) + " " + sent[i].lemma_
        quest2 = "did"+ " " + str(front) + " " + sent[i].lemma_

    elif sent[i].tag_ == "VBZ" and sent[i].lemma_ != "be":
        quest1 = "does"+ " " + find_subject(sent) + " " + sent[i].lemma_
        quest2 = "does"+ " " + str(front) + " " + sent[i].lemma_

    elif sent[i].tag_ == "VBP" or sent[i].tag_ == "VB":
        quest1 = "do"+ " " + find_subject(sent) + " " + sent[i].lemma_
        quest2 = "do"+ " " + str(front) + " " + sent[i].lemma_

    elif sent[i].tag_ == "VBZ" and sent[i].lemma_ == "be":
        quest1 = sent[i].orth_ + " " + find_subject(sent)
        quest2 = sent[i].orth_ + " " + str(front)

    elif sent[i].tag_ == "VBD" and sent[i].lemma_ == "be":
        quest1 = "was"+ " " + find_subject(sent)
        quest2 = "was"+ " " + str(front)

    elif sent[i].tag_ == "VBN" and sent[i].lemma_ == "be":
        quest1 = sent[i].orth_ + " " + find_subject(sent) + " " + sent[i].lemma_
        quest2 = sent[i].orth_ + " " + str(front) + " " + sent[i].lemma_

    elif sent[i].tag_ == "VBN" and sent[i].lemma_ == "have":
        quest1 = sent[i].orth_ + " " + find_subject(sent) + " " + sent[i].lemma_
        quest2 = sent[i].orth_ + " " + str(front) + " " + sent[i].lemma_

    quest1 += " " + str(end) + " ?"
    quest2 += " " + str(end) + " ?"

    return quest1, quest2

# def gscore(question):
#     return float(-len(tool.check(unicode(question))))

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
        who = []
        new = []

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

            if sent[0].text == "This":
                remain = Span(doc, sent.start+1, sent.end-1)
                questions.append(("What " + remain.text + "?", rel+10))
                new.append(("What " + remain.text + "?", rel))

            # What questions
            if (sent.root.lemma_ == "be"):
                for r in sent.root.rights:
                    join = ' '.join(w.text for w in r.subtree)
                    if join[-1] == ",":
                        join = join[:-2]
                    what_question_1 = "What " + sent.root.text + " " + join + "?"
                    # what_question_1 = format_question(what_question_1)
                    # questions.append((what_question_1, rel+gscore(what_question_1)))
                    questions.append((what_question_1, rel))
                    break
                for r in sent.root.lefts:
                    join = ' '.join(w.text for w in r.subtree)
                    if join[-1] == ",":
                        join = join[:-2]
                    what_question_2 = "What " + sent.root.text + " " + join + "?"
                    # what_question_2 = format_question(what_question_2)
                    # questions.append((what_question_2, rel+gscore(what_question_2)))
                    questions.append((what_question_2, rel))

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
                        who_question = "Who " + end.text + "?"
                        # who_question = format_question(who_question)
                        # questions.append((who_question, rel+gscore(who_question)))
                        questions.append((who_question, rel))
                        who.append(who_question)
                    else:
                        who_question = "Who " + end.text + "?"
                        # who_question = format_question(who_question)
                        # questions.append((who_question, rel+gscore(who_question)))
                        questions.append((who_question, rel))
                        who.append(who_question)
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
                    when_question_1 = final[:-1] + "?"
                    # when_question_1 = format_question(when_question_1)
                    questions.append((when_question_1, rel))
                    when.append((when_question_1, rel))
                    break

            # TODO: check if noun after when did
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
                        when_question_2 = final[:-1] + "?"
                        # when_question_2 = format_question(when_question_2)
                        questions.append((when_question_2, rel))
                        when.append((when_question_2, rel))
                    break

            # Where questions
            wheretag = ["GPE", "LOC", "FACILTY", "ORG"]
            for i in range(0, len(sent)-1):
                if (sent[i].ent_type_ in wheretag) and (sent[i-1].ent_type_ not in wheretag) and (sent[i-1].tag_ == "IN"):

                    oneloc =  " " + str(sent[i-1])+ " " + str(sent[i])
                    j = i
                    while j < len(sent)-1 and sent[j+1].ent_type_ in wheretag:
                        oneloc += " " + str(sent[j+1])
                        j = j + 1
                    i = j

                    where_question1 = ""
                    where_question2 = ""

                    for k in range(0, len(sent)-1):
                        if sent[k] == sent.root and (sent[k-1].pos_ == 'VERB'):
                            where_question1 = "Where" + " " + two_verbs(k, sent, doc)[0]
                            where_question2 = "Where" + " " + two_verbs(k, sent, doc)[1]

                        elif sent[k] == sent.root:
                            where_question1 = "Where" + " " + one_verb(k, sent, doc)[0]
                            where_question2 = "Where" + " " + one_verb(k, sent, doc)[1]

                    where_question1 = where_question1.replace(oneloc, "")
                    where_question2 = where_question2.replace(oneloc, "")

                    questions.append((where_question1, rel))
                    questions.append((where_question2, rel))
                    break

        # DO/ DID DOES HAVE WAS IS questions
            for i in range(0, len(sent)-1):
                vquest1 = ""
                vquest2 = ""

                if sent[i] == sent.root and (sent[i-1].pos_ == 'VERB'):
                    if (i > 0):
                        front = Span(doc, sent.start, i+sent.start-1)
                        front_list = str(front).split()
                        if front[0].ent_type_ == "":
                            front_list[0] = front_list[0].lower()
                        str_front = " ".join(front_list)
                    else:
                        font = []
                    end = Span(doc, sent.start + i +1, sent.end-1)
                    # print sent[i-1], sent[i], sent[i-1].tag_, sent[i].tag_
                    if sent[i-1].tag_ == "VBZ" and sent[i].tag_ == "VBN" and sent[i-1].lemma_ != "be"  :
                        vquest1 = "Have"+ " " + find_subject(sent) + " "+ sent[i].lemma_
                        vquest2 = "Have"+ " " + str_front + " "+ sent[i].lemma_

                    elif sent[i-1].tag_ == "VBD" and sent[i].tag_ == "VBN" and sent[i-1].lemma_ == "be":
                        vquest1 = sent[i-1].orth_ + " " + find_subject(sent) + " " + sent[i].orth_
                        vquest2 = sent[i-1].orth_ + " " + str_front + " " + sent[i].orth_

                    elif sent[i-1].tag_ == "VBZ" and sent[i].tag_ == "VBN" and sent[i-1].lemma_ == "be":
                        vquest1 = "Was" + " " + find_subject(sent) + " " + sent[i].orth_
                        vquest2 = "Was" + " " + str_front + " " + sent[i].orth_

                    elif sent[i-1].tag_ == "MD" and sent[i].tag_ == "VB":
                        vquest1 = sent[i-1].orth_ + " " + find_subject(sent) + " " + sent[i].lemma_
                        vquest2 = sent[i-1].orth_ + " " + str_front + " " + sent[i].lemma_

                    vquest1 += " " + str(end) + " ?"
                    vquest2 += " " + str(end) + " ?"
                    # vquest1 = format_question(vquest1)
                    # vquest2 = format_question(vquest2)
                    vquest1 = (two_verbs(i, sent, doc)[0])
                    vquest1 = vquest1[0].capitalize() + vquest1[1:]
                    vquest2 = (two_verbs(i, sent, doc)[1])
                    vquest2 = vquest2[0].capitalize() + vquest2[1:]
                    questions.append((vquest1, rel))
                    questions.append((vquest2, rel))
                    break

                elif sent[i] == sent.root:
                    # print sent[i], sent[i].tag_
                    if (i > 0):
                        front = Span(doc, sent.start, i+sent.start)
                        front_list = str(front).split()
                        if front[0].ent_type_ == "":
                            front_list[0] = front_list[0].lower()
                        str_front = " ".join(front_list)
                    else:
                        font = []
                    end = Span(doc, sent.start+i+1, sent.end-1)
                    vquest1 = ""
                    vquest2 = ""

                    if sent[i].tag_ == "VBD" and sent[i].lemma_ != "be":
                        vquest1 = "Did"+ " " + find_subject(sent) + " " + sent[i].lemma_
                        vquest2 = "Did"+ " " + str_front + " " + sent[i].lemma_

                    elif sent[i].tag_ == "VBZ" and sent[i].lemma_ != "be":
                        vquest1 = "Does"+ " " + find_subject(sent) + " " + sent[i].lemma_
                        vquest2 = "Does"+ " " + str_front + " " + sent[i].lemma_

                    elif sent[i].tag_ == "VBP" or sent[i].tag_ == "VB":
                        vquest1 = "Do"+ " " + find_subject(sent) + " " + sent[i].lemma_
                        vquest2 = "Do"+ " " + str_front + " " + sent[i].lemma_

                    elif sent[i].tag_ == "VBZ" and sent[i].lemma_ == "be":
                        vquest1 = sent[i].orth_ + " " + find_subject(sent)
                        vquest2 = sent[i].orth_ + " " + str_front

                    elif sent[i].tag_ == "VBD" and sent[i].lemma_ == "be":
                        vquest1 = "Was"+ " " + find_subject(sent)
                        vquest2 = "Was"+ " " + str_front

                    elif sent[i].tag_ == "VBN" and sent[i].lemma_ == "be":
                        vquest1 = sent[i].orth_ + " " + find_subject(sent) + " " + sent[i].lemma_
                        vquest2 = sent[i].orth_ + " " + str_front + " " + sent[i].lemma_

                    elif sent[i].tag_ == "VBN" and sent[i].lemma_ == "have":
                        vquest1 = sent[i].orth_ + " " + find_subject(sent) + " " + sent[i].lemma_
                        vquest2 = sent[i].orth_ + " " + str_front + " " + sent[i].lemma_

                    vquest1 += " " + str(end) + " ?"
                    vquest2 += " " + str(end) + " ?"
                    # vquest1 = format_question(vquest1)
                    # vquest2 = format_question(vquest2)
                    vquest1 = (one_verb(i, sent, doc)[0])
                    vquest1 = vquest1[0].capitalize() + vquest1[1:]
                    vquest2 = (one_verb(i, sent, doc)[1])
                    vquest2 = vquest2[0].capitalize() + vquest2[1:]
                    questions.append((vquest1, rel))
                    questions.append((vquest2, rel))
                    break

        pronouns = ["he","He", "she", "his", "her"]
        questions = sorted(questions, key=lambda x: x[1], reverse=True)
        goodQuestions = []
        goodPronouns = []
        for q in questions:
            if (q[0].count(' ') > 3):
                sentence = q[0]
                goodQuestions.append(sentence)
                # matches = tool.check(sentence)
                # if len(matches)==0:
                #     words = q[0].split()
                #     if not any(p == w for w in words for p in pronouns):
                #         goodQuestions.append(sentence)
                #     else:
                #         goodPronouns.append(sentence)

        count = 0
        new = sorted(new, key=lambda x: x[1], reverse=True)
        for i in range(0, len(new)):
            if count < i:
                print new[i][0]

        for i in range(0, 4):
            for j in range(0, len(goodQuestions)/4):
                if count < qNum:
                    count = count+1
                    print goodQuestions[j*4+i]

        for i in range(0, 4):
            for j in range(0, len(goodPronouns)/4):
                if count < qNum:
                    count = count+1
                    print goodPronouns[j*4+i]

txt = NER(textFile)

