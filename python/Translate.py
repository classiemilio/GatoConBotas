import csv, math
from nltk.corpus import brown

class Word:

	def __init__(self, spanish, english, pos):
		self.english = english
		self.spanish = spanish
		self.pos = pos
		
	def isNoun(self):
			return self.pos == 'NOUN' or self.pos == 'PRONOUN'

class Translator:
	
	def __init__(self):
		self.englishRules = []
		self.spanishRules = []
		self.addRules()
		self.bigramCounts = None
		self.trigramCounts = None

	def setNGrams(self):
		print "Building bi/trigram corpus..."
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
		print "Finished building corpus."

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
				word = Word(w, entry[0].split(), entry[1])
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
		
	def dumpSentence(self, sentence):
		print ' '.join(map(lambda word: ' '.join(word.english), sentence))
		
	def addRules(self):
		
		### SPANISH RULES
		def stripSeMeFromVerb(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			for idx,word in enumerate(sentence):
				if (word.spanish == 'se' or word.spanish == 'me') and idx < sentenceLen - 1 and sentence[idx+1].pos == "VERB":
					continue
				newSentence.append(word)
			return newSentence
		self.spanishRules.append(stripSeMeFromVerb)
		
		def flipLoVerb(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.spanish in ['lo', 'la', 'los', 'las'] and idx < sentenceLen - 1 and sentence[idx+1].pos == "VERB":
					newSentence.append(sentence[idx+1])
					newSentence.append(word)
					idx += 2
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.spanishRules.append(flipLoVerb)
		
		### ENGLISH RULES
		def subProperNouns(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if idx < sentenceLen - 3 and word.english == ['the'] and sentence[idx+1].english == ['cat'] and sentence[idx+2].english == ['with'] and sentence[idx+3].english == ['boots']:
					newSentence.append(Word("<PROPER NOUN>", ["Puss in Boots"], "NOUN"))
					idx += 4
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.englishRules.append(subProperNouns)
		
		def separateToFromVerb(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			for idx,word in enumerate(sentence):
				if word.english[0] == 'to' and len(word.english) > 1:
					word.english = word.english[1:]
					newSentence.append(Word('a', ['to'], 'PREP'))
				newSentence.append(word)
			return newSentence
		self.englishRules.append(separateToFromVerb)

		def mergeTo(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			for idx,word in enumerate(sentence):
				if word.english == ['to'] and idx < sentenceLen - 1 and sentence[idx+1].english == ['to']:
					continue
				newSentence.append(word)
			return newSentence
		self.englishRules.append(mergeTo)
		
		def flipNounAdj(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.isNoun() and idx < sentenceLen - 1 and sentence[idx+1].pos == "ADJ":
					newSentence.append(sentence[idx+1])
					newSentence.append(word)
					idx += 2
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.englishRules.append(flipNounAdj)
		
		def flipNounNounVerb(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.isNoun() and idx < sentenceLen - 2 and sentence[idx+1].isNoun() and sentence[idx+2].pos == "VERB":
					newSentence.append(word)
					newSentence.append(sentence[idx+2])
					newSentence.append(sentence[idx+1])
					idx += 3
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		#self.englishRules.append(flipNounNounVerb)
		
		def himToHe(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.english == ['him'] and idx < sentenceLen - 1 and sentence[idx+1].pos == "VERB":
					word.english = ['he']
				newSentence.append(word)
				idx += 1
			return newSentence
		self.englishRules.append(himToHe)
		
		# "No tenia comida" -> "Had no food" ('no' should go after the next word if its a verb)
		def flipNo(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.english == ['no'] and idx < sentenceLen - 1 and sentence[idx+1].pos == "VERB":
					newSentence.append(sentence[idx+1])
					newSentence.append(word)
					idx += 2
				else:
					newSentence.append(word)
					idx += 1
			return newSentence
		self.englishRules.append(flipNo)
		
		def removeEmptyWords(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if len(word.english) > 0:
					newSentence.append(word)
				idx += 1
			return newSentence
		self.englishRules.append(removeEmptyWords)

		def removeExtraneousArticles(sentence):
			if not self.bigramCounts:
				self.setNGrams() 
			newSentence = []
			sentenceLen = len(sentence)
			idx = 0
			while idx < sentenceLen:
				word = sentence[idx]
				if word.pos == 'ARTICLE' and idx < sentenceLen - 2 and idx > 0 and sentence[idx-1].pos != 'PUNCT' and sentence[idx+1].pos != 'PUNCT':
					trigram = sentence[idx - 1].english[-1] + ' ' + ' '.join(word.english) + ' ' + sentence[idx + 1].english[0]
					if self.trigramCounts.get(trigram, 0) > 0:
						newSentence.append(word)
				else:
					newSentence.append(word)
				idx += 1
			return newSentence
		self.englishRules.append(removeExtraneousArticles)
		
	def applyRule(self, rule, sentence):
		return rule(sentence)

	# TODO
	def translate(self, data):
		result = ""
		for sentence in data:
			
			# Apply spanish rules first
			while True:
				oldSentence = sentence
				for rule in self.spanishRules:
					sentence = self.applyRule(rule, sentence)
				if oldSentence == sentence:
					break
			
			# Apply the rules repeatedly until we converge to a single sentence
			while True:
				oldSentence = sentence
				for rule in self.englishRules:
					sentence = self.applyRule(rule, sentence)
				if oldSentence == sentence:
					break

			idx = 0
			for wordGrp in sentence:
				for word in wordGrp.english:
					if word == "<PERIOD>":
						result = result[:-1] + '. '
					elif word == "<COMMA>":
						result = result[:-1] + ', '
					elif word == "<COLON>":
							result = result[:-1] + ': '
					elif word == "<OPENQUOTE>":
						result += '"'
					elif word == "<CLOSEQUOTE>":
						result = result[:-1] + '" '
					elif word == "<OTHERPUNCT>":
						result = result[:-1] + unichr(0xFFFD) + ' '
					else:
						if idx == 0:
							word = word[0].title() + word[1:]
						elif len(result) > 0 and result[-1] == '"':
							word = word[0].title() + word[1:]
						result += word + " "
					idx += 1
			result = result[:-1] + "\n\n"
		return result

	def score(self, data):
		catFile = '../data/cat.txt'
		infile = open(catFile)
		goldLines = infile.readlines()
		infile.close()
		dataLines = data.split('\n\n')
		distortions = []
		missedWords = 0
		for goldLine, dataLine in zip(goldLines, dataLines):
			def cleanup(word): return word.strip('.,:"\n').lower()
			goldLine = map(cleanup, goldLine.split())
			dataLine = map(cleanup, dataLine.split())
			distortions.append([])
			
			def getNearestIdx(line, queryWord, queryIdx):
				minDist = None
				minIdx = None
				for idx,word in enumerate(line):
					curDist = math.fabs(queryIdx - idx)
					if queryWord == word and (minDist == None or curDist < minDist):
						minDist = curDist
						minIdx = idx
				return minIdx
			
			lastGoldIdx = 0
			for dataIdx, dataWord in enumerate(dataLine):
				curGoldIdx = getNearestIdx(goldLine, dataWord, dataIdx)
				if curGoldIdx != None:
					distortions[-1].append(curGoldIdx - lastGoldIdx - 1)
					lastGoldIdx = curGoldIdx
				else:
					missedWords += 1

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
