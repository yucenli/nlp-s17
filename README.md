# nlp-s17
Question Answering

## mostCommonNNP 
  Gives the most common proper nouns in the given text

  Specify the text and the number of most common proper nouns desired
  
  Example:
  
	python3 mostCommonNNP.py set1/a1.txt 20


## txt_ner.py
  Specific to the txt files in the data set

  Example:

	import txt_ner

	# Create an instance of the desired txt file
	txt = txt_ner.NER("set1/a1.txt")

	# Prints the ith sentence along with its part-of-speech tags and named entities
	txt.printTag(i)  

	# Draws the corresponding tree of the tagged sentence
	txt.drawTree(i)  


## ner.py
  Tags and chunks generic sentence

  Specifiy the sentence as a string

  Example:

	import ner

	# Create an instance of the sample sentence
	sentence = ner.NER("Abraham Lincoln was born in Hodgenville Kentucky.")

	# Prints the sentence along with its part-of-speech tags and named entities
	sentence.printTag()  

	# Draws the corresponding tree of the tagged sentence
	sentence.drawTree()  
