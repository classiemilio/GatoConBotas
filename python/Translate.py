import csv, math

class Word:

	def __init__(self, spanish, english):
		self.english = english
		self.spanish = spanish

class Translator:
	
	def __init__(self):
		self.rules = []
		self.addRules()
	

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
			lineSpl = map(lambda word: word.strip('.,:"').lower(), line.split())
			for w in lineSpl:
				word = Word(w, self.dict.get(w, 'NOTFOUND'))
				sentence.append(word)
			data.append(sentence)
		return data
		
	def addRules(self):
		
		def mergeTo(sentence):
			newSentence = []
			sentenceLen = len(sentence)
			for idx,word in enumerate(sentence):
				if word.english == 'to' and idx < sentenceLen - 1 and sentence[idx+1].english.startswith('to'):
					continue
				newSentence.append(word)
			return newSentence
		self.rules.append(mergeTo)
		
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
				result += word.english + " "
			result = result[:-1] + ". \n\n"
		return result

	def score(self, data):
		catFile = '../data/cat.txt'
		infile = open(catFile)
		lines = infile.readlines()
		infile.close()
		data = data.split(' \n\n')
		for line, datum in zip(lines, data):
			line = line.strip('.,:"\n')
			line = line.split()
			datum = datum.split()
			totalDistance = 0
			missedWords = 0
			for i, d in enumerate(datum):
				minDistance = 100000
				for j, l in enumerate(line):
					if d.lower() == l.lower():
						curDistance = math.fabs(i-j)
						if curDistance < minDistance: minDistance = curDistance
				if minDistance == 100000: 
					missedWords += 1
				else:
					totalDistance += minDistance 
		print 'Total error distance: ' + str(totalDistance)
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
