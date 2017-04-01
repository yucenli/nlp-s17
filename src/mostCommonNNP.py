import nltk
import os
import re
import sys
from collections import Counter


def main():

    inputs = sys.argv[1:]
    txt_path = inputs[0]
    n = int(inputs[1])

    cur_path = os.path.dirname(__file__)
    rel_path = '../data/' + txt_path
    f_path = os.path.join(cur_path, rel_path)

    with open(f_path, 'r') as f:
        txt = f.read().replace('\n', '')

    mostCommonNNP(txt, n)


# Get the n most common NNP (Proper Nouns) from the text
def mostCommonNNP(text, n):

    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    tagged_count = Counter(tagged)
    tagged_count_nnp = Counter()

    for tag in tagged_count:
        if tag[1] == 'NNP':
            tagged_count_nnp[tag] = tagged_count[tag]

    print(tagged_count_nnp.most_common(n))









if __name__ == '__main__':
    main()