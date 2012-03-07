import csv

class Word:

	def __init__(self, spanish, english):
		self.english = english
		self.spanish = spanish

class Translator:

	def readInDictionary(self, file):
		infile = open(file, 'rb')
		self.dict = {}
		reader = csv.reader(infile)
		for row in reader:
			self.dict[row[0]] = row[1]
		infile.close()
		

	def readInData(self, file):
		infile = open(file)
		lines = infile.readlines()
		infile.close()
		data = []
		for line in lines:
			sentence = []
			lineSpl = line.split()
			for w in lineSpl:
				word = Word(w, self.dict.get(w, 'NOTFOUND'))
				print word.spanish + "   " + word.english
				sentence.append(word)
			data.append(sentence)
		return data

	# TODO
	def translate(self, data):
		return ''

if __name__ == '__main__':
	gatoFile = '../data/gato.txt'
	dictFile = '../data/dict.csv'
	translator = Translator()
	translator.readInDictionary(dictFile)
	data = translator.readInData(gatoFile)
	translated = translator.translate(data)
