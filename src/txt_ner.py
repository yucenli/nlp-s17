import nltk
import os
import re


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

        sentence_regex = "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        regex = re.compile(sentence_regex)

        sentences = [x for x in txt if regex.search(x)]
        all_sentences = []
        for sentence in sentences:
            all_sentences += re.split(sentence_regex, sentence)

        self.sentences = all_sentences

        tagged_sentences = []

        for sentence in self.sentences:
            ne_tree = nltk.chunk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)))
            iob_tagged = nltk.chunk.tree2conlltags(ne_tree)
            tagged_sentences.append(iob_tagged)

        self.tagged_sentences = tagged_sentences

    def printTag(self, i):
        print(self.tagged_sentences[i])

    def drawTree(self, i):
        ne_tree = nltk.chunk.conlltags2tree(self.tagged_sentences[i])
        ne_tree.draw()
