from __future__ import unicode_literals

import spacy
from nltk import Tree
from spacy.en import English
parser = English()

sentence = "One of Dempsey's passions outside of soccer is hip-hop"

doc = parser(sentence)
for sent in doc.sents:
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

def tok_format(tok):
    return "_".join([tok.orth_, tok.tag_])

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)

[to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]

