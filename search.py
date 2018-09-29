import operator
import re 
import os
from stopWords import StopWords
from Stemmer import Stemmer

stop_words = StopWords()
stop_words.readStopWords()
stemmer = Stemmer('english')
max_line_len = 2 ** 20
def line_binary_search(filename, matchvalue, max_line_len,key=lambda val: val):

    start = pos = 0
    end = os.path.getsize(filename)
    with open(filename, 'rb') as fptr:
        for rpt in xrange(50):
            last = pos
            pos = start + ((end - start) / 2)
            fptr.seek(pos)
            fptr.readline()
            line = fptr.readline()
            linevalue = key(line)
            if linevalue == matchvalue or pos == last:
                while True:
                    fptr.seek(-max_line_len, 1)
                    fptr.readline()
                    if matchvalue != key(fptr.readline()):
                        break
                for rpt in xrange(max_line_len):
                    line = fptr.readline()
                    linevalue = key(line)
                    if matchvalue == linevalue:
                        break
                else:
                    return []
                results = []
                while linevalue == matchvalue:
                    results.append(line)
                    line = fptr.readline()
                    linevalue = key(line)
                return results
            elif linevalue < matchvalue:
                start = fptr.tell()
            else:
                assert linevalue > matchvalue
                end = fptr.tell()
        else:
            raise RuntimeError('binary search failed')

def makeDict(filename , qt):
    max_line_len = 2 ** 20
    while(1):
        try:
            qtDocs = line_binary_search(filename, qt,max_line_len, lambda val : val.split(':')[0])
            break
        except:
            max_line_len = max_line_len/2 
    if len(qtDocs)==1: 
        s1 = qtDocs[0].split(':')
        s2 = s1[1].split('|')
        for qtd in s2:
            s3 = qtd.split(' ')
            if(len(s3)>1):
                if(int(s3[0]) in qdocs):
                    qdocs[int(s3[0])] = float(s3[1]) + qdocs[int(s3[0])] 
                else:    
                    qdocs[int(s3[0])] = float(s3[1])

max_no_doc = 10
inp = raw_input('query plz:->')

qterms = inp.split(' ')

qdocs = {}
for qterm in qterms:
    if(':' in qterm):    
        s1 = qterm.split(':')
        s1[1] = stemmer.stemWord(s1[1].lower())
        if not stop_words.isStopWord(s1[1]):
            if(s1[0]=='t'):
                makeDict('data/title.txt',s1[1])
            elif(s1[0]=='i'):
                makeDict('data/infobox.txt',s1[1])
            elif(s1[0]=='e'):
                makeDict('data/external.txt',s1[1])
            elif(s1[0]=='c'):
                makeDict('data/category.txt',s1[1])
            elif(s1[0]=='b'):
                makeDict('data/body.txt',s1[1])
            elif(s1[0]=='r'):
                makeDict('data/reference.txt',s1[1])
    else:
        qterm = stemmer.stemWord(qterm.lower())
        if not stop_words.isStopWord(qterm):
            makeDict('data/all.txt',qterm)

sorted_x = sorted(qdocs.items(), key=operator.itemgetter(1) , reverse=True)
print sorted_x

no_doc = 0
result = []
for i in sorted_x:
    max_line_len = 2 ** 30
    while(1):
        try:
            titleL = line_binary_search('titles', str(i[0]) ,max_line_len, lambda val : val.split(':')[0])
            break
        except:
            max_line_len = max_line_len/2 
            
    print titleL
    
    if len(titleL)>0 :
            

        dicId = titleL[0].split(':')
        
        titleName = dicId[1]
        
        result.append((dicId[0],titleName))

        no_doc = no_doc + 1
        if(no_doc >= max_no_doc):
            break

# for d , t in result:
#     print  t 
