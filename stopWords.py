from Stemmer import Stemmer

stemmer = Stemmer('english')

class StopWords:
    "Load stop words from stopWords.txt to a set"

    def __init__(self):
        self.stopWordsList = []
        self.stopWordsSet = set()

    def readStopWords(self):
        with open("./stopWords.txt") as input_file:
            for input_line_raw in input_file:
                input_tokens = input_line_raw.split(', ')
                self.stopWordsList.extend(input_tokens)
                input_tokens = list(map(stemmer.stemWord, input_tokens))
            self.stopWordsSet = set(self.stopWordsList)

    def isStopWord(self, token):
        try:
            if token in self.stopWordsSet or len(token) < 2 or len(token) > 20:
                return True
            else:
                return False
        except IOError:
            print "StopWordsSet not found"