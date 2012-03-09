import csv, math
from nltk.corpus import brown

class Word:

	def __init__(self, spanish, english, pos):
		self.english = english
		self.spanish = spanish
		self.pos = pos

class Translator:
	
	def __init__(self):
		self.rules = []
		self.addRules()
		self.bigramCounts = None
		self.trigramCounts = None

	def setNGrams(self):
		self.bigramCounts = {}
		self.trigramCounts = {}
		bWords = brown.words()
		bLen = len(bWords)
		for i in range(bLen):
			word = bWords[i]
			if i + 1 < bLen:
				bigram = word.lower() + ' ' + bWords[i + 1].lower()
				self.bigramCounts[bigram] = self.bigramCounts.get(bigram, 0) + 1
				if i + 2 < bLen:
					trigram = bigram + ' ' + bWords[i + 2]
					self.trigramCounts[trigram] = self.trigramCounts.get(trigram, 0) + 1

	def readInDictionary(self, file):
		infile = open(file, 'rb')
		self.dict = {}
		reader = csv.reader(infile)
		for row in reader:
			self.dict[row[0]] = (row[1],row[2])
		infile.close()
		

	def readInData(self, file):
		infile = open(file)
		lines = infile.readlines()
		infile.close()
		data = []
		for line in lines:
			sentence = []
			lineSpl = map(lambda word: word.lower(), line.split())
			lineSpl = self.splitPunct(lineSpl)
			for w in lineSpl:
				entry = self.dict.get(w, ('NOTFOUND', 'UNKNOWN'))
				word = Word(w, entry[0], entry[1])
				sentence.append(word)
			data.append(sentence)
		return data
		
	def splitPunct(self, sentence):
		newSentence = []	
		for word in sentence:
			newWords = []
			while 1 in [c == word[-1:] for c in ['.', ',', ':', '"']]:
				if word[-1:] == '.':
					newWords.insert(0, "<PERIOD>")
				elif word[-1:] == ',':
					newWords.insert(0, "<COMMA>")
				elif word[-1:] == ':':
					newWords.insert(0, "<COLON>")
				elif word[-1:] == '"':
					newWords.insert(0, "<CLOSEQUOTE>")
				else:
					newWords.insert(0, "<OTHERPUNCT")
				word = word[:-1]
			newWords.insert(0, word)
			if (newWords[0][0] == '"'):
				newWords[0] = newWords[0][1:]
				newWords.insert(0, "<OPENQUOTE>")
			newSentence.extend(newWords)
		return newSentence
		
	def addRules(self):
		
		def mergeTo(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			for idx,word in enumerate(sentence):
				if word.english == 'to' and idx < sentenceLen - 1 and sentence[idx+1].english.startswith('to '):
					sentence[idx+1].english = sentence[idx+1].english[3:]
				newSentence.append(word)
			return newSentence
		self.rules.append(mergeTo)
		
		def flipNounAdj(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.pos == 'NOUN' and idx < sentenceLen - 2 and sentence[idx+1].pos == "ADJ":
					newSentence.append(sentence[idx+1])
					newSentence.append(word)
					idx += 2
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.rules.append(flipNounAdj)

		# "No tenia comida" -> "Had no food" ('no' should go after the next word if its a verb)
		def flipNo(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.english == 'no' and idx < sentenceLen - 2 and sentence[idx+1].pos == "VERB":
					newSentence.append(sentence[idx+1])
					newSentence.append(word)
					idx += 2
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.rules.append(flipNo)

		def removeExtraneousArticles(sentence):
			if not self.bigramCounts:
				self.setNGrams() 
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.pos == 'ARTICLE' and idx < sentenceLen - 2 and idx > 0:
					trigram = sentence[idx - 1].english + ' ' + word.english + ' ' + sentence[idx + 1].english
					if self.trigramCounts.get(trigram, 0) > 0:
						newSentence.append(word)
				else:
					newSentence.append(word)
				idx += 1
			return newSentence
		self.rules.append(removeExtraneousArticles)
		
		def flipHimVerb(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.english == 'him' and idx < sentenceLen - 1 and sentence[idx+1].pos == "VERB":
					newSentence.append(sentence[idx+1])
					newSentence.append(word)
					idx += 2
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.rules.append(flipHimVerb)
		
	def applyRule(self, rule, sentence):
		return rule(sentence)

	# TODO
	def translate(self, data):
		result = ""
		for sentence in data:
			
			for rule in self.rules:
				sentence = self.applyRule(rule, sentence)

			for idx,word in enumerate(sentence):
				if idx == 0:
					word.english = word.english[0].title() + word.english[1:]
				if word.english == "<PERIOD>":
					result = result[:-1] + '. '
				elif word.english == "<COMMA>":
					result = result[:-1] + ', '
				elif word.english == "<COLON>":
						result = result[:-1] + ': '
				elif word.english == "<OPENQUOTE>":
					result += '"'
				elif word.english == "<CLOSEQUOTE>":
					result = result[:-1] + '" '
				elif word.english == "<OTHERPUNCT>":
					result = result[:-1] + unichr(0xFFFD) + ' '
				else:
					result += word.english + " "
			result = result[:-1] + "\n\n"
		return result

	def score(self, data):
		catFile = '../data/cat.txt'
		infile = open(catFile)
		lines = infile.readlines()
		infile.close()
		data = data.split('\n\n')
		distortions = []
		missedWords = 0
		for line, datum in zip(lines, data):
			line = line.strip('.,:"\n').split()
			datum = datum.strip('.,:"\n').split()
			distortions.append([0])
			for i, d in enumerate(datum):
				minDistance = 100000
				for j, l in enumerate(line):
					if d.lower() == l.lower():
						curDistance = math.fabs(i-j)
						if curDistance < minDistance: minDistance = curDistance
				if minDistance == 100000: 
					missedWords += 1
					distortion = 0
				else:
					distortion = minDistance - distortions[-1][-1] - 1
				distortions[-1].append(distortion)
		distortions = [item for sublist in distortions for item in sublist]
		print 'Total distortion: ' + str(reduce(lambda x, y: x+math.fabs(y), distortions))
		print 'Words in gold that are not in gato: ' + str(missedWords)
			

if __name__ == '__main__':
	gatoFile = '../data/gato.txt'
	dictFile = '../data/dict.csv'
	translator = Translator()
	translator.readInDictionary(dictFile)
	data = translator.readInData(gatoFile)
	translated = translator.translate(data)
	print translated
	translator.score(translated)
