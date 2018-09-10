import operator
import re 
import os
def line_binary_search(filename, matchvalue, key=lambda val: val):
    """
    Binary search a file for matching lines.
    Returns a list of matching lines.
    filename - path to file, passed to 'open'
    matchvalue - value to match
    key - function to extract comparison value from line
 
    parser = lambda val: int(val.split('\t')[0].strip())
    line_binary_search('sd-arc', 63889187, parser)
    ['63889187\t3592559\n', ...]
    """
 
    # Must be greater than the maximum length of any line.
 
    max_line_len = 2 ** 12
 
    start = pos = 0
    end = os.path.getsize(filename)
 
    with open(filename, 'rb') as fptr:
 
        # Limit the number of times we binary search.
 
        for rpt in xrange(50):
 
            last = pos
            pos = start + ((end - start) / 2)
            fptr.seek(pos)
 
            # Move the cursor to a newline boundary.
 
            fptr.readline()
 
            line = fptr.readline()
            linevalue = key(line)
 
            if linevalue == matchvalue or pos == last:
 
                # Seek back until we no longer have a match.
 
                while True:
                    fptr.seek(-max_line_len, 1)
                    fptr.readline()
                    if matchvalue != key(fptr.readline()):
                        break
 
               # Seek forward to the first match.
 
                for rpt in xrange(max_line_len):
                    line = fptr.readline()
                    linevalue = key(line)
                    if matchvalue == linevalue:
                        break
                else:
                    # No match was found.
 
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
    print 'a'
    qtDocs = line_binary_search(filename, qt, lambda val : val.split(':')[0])
    print qtDocs
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
        print s1
        if(s1[0]=='t'):
            makeDict('title.txt',s1[1])
        elif(s1[0]=='i'):
            makeDict('infobox.txt',s1[1])
        elif(s1[0]=='e'):
            makeDict('external.txt',s1[1])
        elif(s1[0]=='c'):
            makeDict('category.txt',s1[1])
        elif(s1[0]=='b'):
            makeDict('body.txt',s1[1])
        elif(s1[0]=='r'):
            makeDict('reference.txx',s1[1])
    else:
        makeDict('all.txt',qterm)

sorted_x = sorted(qdocs.items(), key=operator.itemgetter(1) , reverse=True)
no_doc = 0
for i in sorted_x:
    titleL = line_binary_search('titles', str(i[0]) , lambda val : val.split(':')[0])
    title = titleL[0].split(':')

    no_doc = no_doc + 1
    if(no_doc >= max_no_doc):
        break

print sorted_x