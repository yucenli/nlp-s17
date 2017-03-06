# nlp-s17
Question Answering

## mostCommonNNP 
  Gives the most common proper nouns in the given text

  Specify the text and the number of most common proper nouns desired
  
  Example:
  
	python3 mostCommonNNP.py set1/a1.txt 20


## txt_ner.py
  Specific to the txt files in the data set

## ner.py
  Tags and chunks generic sentence

  Specifiy the sentence as a string

  Example:

 	python3   

	  ```python
	  	import ner

	  	sentence = ner.NER("Abraham Lincoln was born in Hodgenville, Kentucky.")

	  	sentence.printTag()  # Prints the sentence along with its part-of-speech tags and named entities

	  	sentence.drawTree()  # Draws the corresponding tree of the tagged sentence
	  ```
