import nltk


class NER(object):
    """docstring for NER"""
    def __init__(self, sentence):
        super(NER, self).__init__()
        self.sentence = sentence
        self.tokens = nltk.word_tokenize(sentence)
        ne_tree = nltk.chunk.ne_chunk(nltk.pos_tag(self.tokens))
        iob_tagged = nltk.chunk.tree2conlltags(ne_tree)

        self.tagged_sentence = iob_tagged

    def printTag(self):
        print(self.tagged_sentence)

    def drawTree(self):
        ne_tree = nltk.chunk.conlltags2tree(self.tagged_sentence)
        ne_tree.draw()
