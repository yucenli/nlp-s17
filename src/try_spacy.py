from __future__ import unicode_literals

import spacy
from nltk import Tree
from spacy.en import English
parser = English()

def tok_format(tok):
    return "_".join([tok.orth_, tok.tag_])

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)



sentence = "Is the battery made by Volta credited as the first electromechanical cell?"

doc = parser(sentence)

print sentence
[to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]

for sent in doc.sents:

    for token in sent:
        if token.ent_type_ == "DATE":
            print token


    print sent.root
    if (sent.root.lemma_ == "be"):
        print sent
        for r in sent.root.rights:
            print "What " + sent.root.text + " " + ' '.join(w.text for w in r.subtree) + "?"
            break
        right = ""
        for r in sent.root.lefts:
            right = "What " + sent.root.text + " " + ' '.join(w.text for w in r.subtree) + "?"
        print right

