import ner
import txt_ner
from nltk.stem.wordnet import WordNetLemmatizer


def filterSentencesByWord(sentences, taggedSentences, mWord):
    filteredSentences = []
    filteredTaggedSentences = []
    for sentence, tSentence in zip(sentences, taggedSentences):
        for wordTag in tSentence:
            if wordTag[0] == mWord:
                filteredSentences.append(sentence)
                filteredTaggedSentences.append(tSentence)
                break
    return (filteredSentences, filteredTaggedSentences)


auxVerbs = ["have", "be", "do"]

question = "Where was Clint Dempsey born?"

txt = txt_ner.NER("set1/a1.txt")
sentences = txt.sentences
taggedSentences = txt.tagged_sentences

q = ner.NER(question)
q.printTag()

for wordTag in q.tagged_sentence:
    word = wordTag[0]
    lemWord = WordNetLemmatizer().lemmatize(word, 'v')
    tag = wordTag[1]
    # if tag == 'NNP':
    #     taggedSentences = filterSentencesByWord(taggedSentences, word)
    if (tag[:2] == 'VB') and (lemWord not in auxVerbs):
        sentences, taggedSentences = filterSentencesByWord(sentences, taggedSentences, word)

print(sentences)
print(taggedSentences)


# answer = "Clint Dempsey was born in Nacogdoches, Texas"

# txt = ner.NER(answer)
# txt.printTag()


# words = ["has", "have", "had", "having", "am", "is", "are",
#          "was", "were", "being", "been", "does", "do", "did"]

# for word in words:
#     print(word + "-->" + WordNetLemmatizer().lemmatize(word, 'v'))
