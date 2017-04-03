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

        # for sent in doc.sents:
        #     print(sent.string)
        #     if (sent.root.lemma_ == "be"):
        #         print sent
        #         for r in sent.root.rights:
        #             print "What " + sent.root.text + " " + ' '.join(w.text for w in r.subtree) + "?"
        #             break
        #         right = ""
        #         for r in sent.root.lefts:
        #             right = "What " + sent.root.text + " " + ' '.join(w.text for w in r.subtree) + "?"
        #         print right
        #         print " "
        #
        # # Who questions
        # subject = ["he", "she", "they"]
        #
        # for sent in doc.sents:
        #     for i in range(0, len(sent)-1) :
        #         if sent[i].dep_ == "nsubj" and sent[i].ent_type_ == "PERSON" or sent[i].text in subject:
        #             print sent
        #             hi = Span(doc, sent.start, i+sent.start)
        #             i = i+1
        #             while i < len(sent)-1:
        #                 if sent[i].ent_type_ == "PERSON":
        #                     i = i+1
        #                 elif sent[i].dep_ == "nsubj":
        #                     i = i+1
        #                 else:
        #                     break
        #             end = Span(doc, i + sent.start, sent.end-1)
        #             if (hi.text == ""):
        #                 print "Who " + end.text + "?"
        #             else:
        #                 print hi.text + " who " + end.text + "?"
        #             print ""
        #             break
        #
        # # When questions
        # for sent in doc.sents:
        #     for i in range(0, len(sent)-1):
        #         if (sent[i].ent_type_ == "DATE" and sent[i].pos_ != "ADJ"):
        #             print sent
        #             hi = Span(doc, sent.start, i+sent.start)
        #             head = sent[i].head
        #             while i < len(sent) - 1 and (sent[i].ent_type_ == "DATE" or sent[i].pos_ == "PUNCT"):
        #                 i = i+1
        #             end = Span(doc, i + sent.start, sent.end-1)
        #             verb = sent[i]
        #             for t in sent.root.lefts:
        #                 verb = t
        #             if verb.lemma_ == "be":
        #                 final = "When was "
        #             else:
        #                 final = "When did "
        #             for token in end:
        #                 if verb.lemma_ == "be" and token.lemma_ == "be":
        #                     final = final
        #                 elif verb.lemma_ != "be" and token == sent.root:
        #                     final = final + sent.root.lemma_ + " "
        #                 else:
        #                     final = final + token.orth_ + " "
        #             print final[:-1] + "?"
        #             print ""
        #             break

        # --------------------------------------------------------------------
        # Where questions
        for sent in doc.sents:
            # possible_locations = []
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

                    for t in sent.root.lefts:
                        if t.pos_ == "VERB":
                            verb = t

                    if verb.lemma_ == "be":
                        final = "Where was "
                    elif verb.tag_ == "VB":
                        final = "Where do "
                    elif verb.tag_ == "VBP":
                        final = "Where have "
                    else:
                        final = "Where did "

                    for r in sent.root.rights:
                        subject = ''
                        for l in sent.root.lefts:
                            if l.right_edge.dep_=='nsubj':
                                subject = str(l.right_edge)
                                break
                            else:
                                subject =  ' '.join(w.text for w in l.subtree)
                        final += subject + " " + verb.lemma_ + " " + ' '.join(w.text for w  in r.subtree) + " ?"
                        break

                    final = final.replace(oneloc, "")
                    print final[:-1] + "?"
                    print ""
                    break

        # DO/ DID DOES HAVE questions
        for sent in doc.sents:
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
                    elif sent.root.tag_ == 'VBN':
                        v_question = 'Have'
                    elif sent.root.tag_ == 'VBP':
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
                    v_question += " " + subject + " " + sent.root.lemma_ + " " +' '.join(w.text for w in r.subtree) + " " +'?'
                    break

                print v_question
                print ""
                break

        # Is Was Were Questions
        for sent in doc.sents:
            if (sent.root.lemma_ == "be"):
                print sent
                for r in sent.root.rights:
                    if sent.root.text == '\'s':
                        isquest1 == 'Is'
                    else:
                        isquest1 = sent.root.text.capitalize()
                    for l in sent.root.lefts:
                        isquest1 += " " + ' '.join(w.text for w in l.subtree)
                    isquest1 += ' ' +' '.join(w.text for w in r.subtree) + " " +'?'
                    break
                print isquest1
                print ""
                break


txt = NER("set1/a5.txt")
#
#
#
#
#
#
