textFile = open('gato.txt', 'r')
dictFile = open('dict.csv', 'w')

text = textFile.read()
words = sorted(list(set(map(lambda word: word.strip('.,:"').lower(), text.split()))))

for word in words:
    dictFile.write(word + ',\n')

textFile.close()
dictFile.close()