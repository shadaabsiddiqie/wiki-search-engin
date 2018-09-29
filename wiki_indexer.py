import xml.etree.ElementTree as etree
import sys
import itertools
import os
import re
import math
import heapq
import subprocess
from stopWords import StopWords
from Stemmer import Stemmer

reload(sys)
sys.setdefaultencoding('utf8')

argv = sys.argv

PATH_WIKI_XML = './'
FILENAME_WIKI = './wiki-search-small.xml'
ENCODING = "utf-8"

stop_words = StopWords()
stop_words.readStopWords()
stemmer = Stemmer('english')
freq = {}
doc_freq = {}
titles = {}
category_detection = re.compile(u"\[\[Category:(.*?)\]\]", re.M)
file_cntr = 0
file_step = 1000

def getCategories(text):
    cate = []
    matches = re.finditer(category_detection, text)
    if matches:
        for match in matches:
            temp = match.group(1).split("|")
            if temp:
                cate.extend(temp)
    data = ' '.join(cate)
    tokenisedWords = re.findall("\d+|[\w]+", data)
    tokenisedWords = [key.encode('utf-8') for key in tokenisedWords]
    return tokenisedWords

def getExternalLinks(text):
    links = []
    data = text
    lines = data.split("==External links==")
    if len(lines) > 1:
        lines = lines[1].split("\n")
        for i in xrange(len(lines)):
            if '* [' in lines[i] or '*[' in lines[i]:
                word = ""
                temp = lines[i].split(' ')
                temp = temp[2:]
                word = [key for key in temp if 'http' not in temp]
                word = ' '.join(word).encode('utf-8')
                links.append(word)
    data = ' '.join(links)
    tokenisedWords = re.findall("\d+|[\w]+", data)
    tokenisedWords = [key.encode('utf-8') for key in tokenisedWords]
    return tokenisedWords

def getExternalReferences(text):
    data = elem.text
    lines = data.split("==References==")
    external_references = []
    if len(lines) > 1:
        external_references = re.findall("\d+|[\w]+", lines[1])
        external_references = [key.encode('utf-8') for key in external_references]
    return external_references

def write_to_disk(cntr):
    file = open('./index/file'+str(cntr), "w")
    for key in sorted(freq.keys()):
        file.write(str(key)+":"+str(freq[key])+'\n')

def process_body_text(text):
    tokens = re.split(r"[^A-Za-z]+", text)
    temp = []
    for w in tokens:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp

def process_lists(text):
    temp = []
    tokens = re.split(r"[^A-Za-z]+", text)
    for w in tokens:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp

def process_lists_categories(text):
    temp = []
    for w in text:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp

def process_references(text):
    temp = []
    for w in text:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp

def strip_tag_name(t):
    t = elem.tag
    idx = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t

def update_dict(docid):
    for key in doc_freq:
        if key == '':
            continue
        t = doc_freq[key][0]
        i = doc_freq[key][1]
        e = doc_freq[key][2]
        c = doc_freq[key][3]
        b = doc_freq[key][4]
        r = doc_freq[key][5]
        strg = 'd'+str(id)

        # title infobox ext-links catogaries bodytext referance
        if t > 0:
            strg = strg + 't' + str(t)
        if i > 0:
            strg = strg + 'i' + str(i)
        if e > 0:
            strg = strg + 'e' + str(e)
        if c > 0:
            strg = strg + 'c' + str(c)
        if b > 0:
            strg = strg + 'b' + str(b)
        if r > 0:
            strg = strg + 'r' + str(r)
        
        if key not in freq:
            freq[key] = strg
        else:
            freq[key] = freq[key] + '|' +  strg

def write_title_disk():
    file = open('titles', "w")
    for key in sorted(titles.keys()):
        file.write(str(key)+":"+str(titles[key])+'\n')

pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)

totalCount = 0
articleCount = 0
title = None

# sort variables
n_files = len(os.listdir('index'))
fds = {}
n_lines = {}
lines_read = {}
heap = []
heapq.heapify(heap)

def get_key(val):
    return int(re.search('[0-9]+', val).group())

def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

def sortDiffFiles():
    
    for i in range(n_files):
        file_name = "index/file" + str(i)
        fds[i] = open(file_name, "r")
        n_lines[i] = file_len(file_name)
        lines_read[i] = 0

    
    finalIndexFileName = "finalIndex.txt"
    fd = open(finalIndexFileName, "w")

    for i in range(n_files):
        file_no = i
        if lines_read[file_no] < n_lines[file_no]:
            line = fds[file_no].readline()
            cols = line.split(":")
            token = cols[0]
            content = cols[1]
            if content[len(content)-1] == "\n":
                content = content[:-1]
            heapq.heappush(heap, (token, content, file_no))
            lines_read[file_no] += 1
  

    previous_line = ("", "")
    while len(heap):
        token, content, file_no = heapq.heappop(heap)
        previous_token, previous_content = previous_line
        
        if previous_token == token:        
            content = previous_content + "|" + content
            content = content.split("|")        
            content.sort(key=get_key)
            content = '|'.join(content)
        elif previous_token != "":
            fd.write(previous_token+":"+previous_content+"\n")
        previous_line = (token, content)
            
        if lines_read[file_no] < n_lines[file_no]:
            line = fds[file_no].readline()
            cols = line.split(":")
            token = cols[0]
            content = cols[1]
            if content[len(content)-1] == "\n":
                content = content[:-1]
            heapq.heappush(heap, (token, content, file_no))
            lines_read[file_no] += 1


        if len(heap) == 0:
            fd.write(previous_token+":"+previous_content+"\n")

    fd.close()

    for i in range(n_files):
        fds[i].close()

for event, elem in etree.iterparse(argv[1], events=('start', 'end')):
    tname = strip_tag_name(elem.tag)
    if event == 'start':
        if tname == 'page':
            title = ''
            id = -1
            redirect = ''
            inrevision = False
            ns = 0
            doc_freq.clear()
        elif tname == 'revision':
            inrevision = True
    else:
        if tname == 'id' and not inrevision:
            id = int(elem.text)
            titles[id] = title
        elif tname == 'title':
            title = str(elem.text)
            title_terms = process_lists(title)
            for w in title_terms:
                if w not in doc_freq:
                    doc_freq[w] = (1, 0, 0, 0, 0, 0)
                else:
                    hold = doc_freq[w]
                    doc_freq[w] = (hold[0]+1, hold[1], hold[2], hold[3], hold[4], hold[5])
        elif tname == 'page':
            totalCount += 1
            # print(totalCount)
            if totalCount % file_step == 0:
                write_to_disk(file_cntr)
                elem.clear()
                freq.clear()
                doc_freq.clear()
                file_cntr = file_cntr + 1
                # print('file_cntr: ' + str(file_cntr))
        elif tname == 'text':

            if elem.text is not None:
                templinks = getExternalLinks(elem.text)
                external_links = templinks

                categories = getCategories(str(elem.text))

                references = getExternalReferences(str(elem.text))

                body_terms = process_body_text(str(elem.text))
                for w in body_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 0, 0, 0, 1, 0)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0], hold[1], hold[2], hold[3],hold[4]+1,hold[5])

                link_terms = process_lists_categories(external_links)
                for w in link_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 0, 1, 0 ,0 , 0)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0], hold[1], hold[2]+1, hold[3] ,hold[4] ,hold[5])

                references_terms = process_references(external_links)
                for w in references_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 0, 0, 0, 0, 1)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0], hold[1], hold[2], hold[3], hold[4], hold[5]+1)


                cat_terms = process_lists_categories(categories)
                for w in cat_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 0, 0, 1, 0, 0)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0], hold[1], hold[2], hold[3]+1, hold[4], hold[5])

                update_dict(id)
        
        elem.clear()

write_title_disk()


#sourting main index
sortDiffFiles()

f = open('finalIndex.txt',"r")

lenght_file = file_len('finalIndex.txt')

f_finalTFIDF = open('data/all.txt','w')
f_tTFIDF = open('data/title.txt','w')
f_iTFIDF = open('data/infobox.txt','w')
f_eTFIDF = open('data/external.txt','w')
f_cTFIDF = open('data/category.txt','w')
f_bTFIDF = open('data/body.txt','w')
f_rTFIDF = open('data/reference.txt','w')

for i in range(lenght_file):
    line = f.readline()
    s1 = line.split(':')
    term = s1[0]
    s2 = s1[1].split('|')
    noDoc = len(s2)
    term_data = ''
    term_data_t = ''
    term_data_i = ''
    term_data_e = ''
    term_data_c = ''
    term_data_b = ''
    term_data_r = ''
    
    for doc in s2:

        doc_data = []
        tId = 0 
        iId = 0
        eId = 0
        cId = 0
        bId = 0
        rId = 0
        docId = int(re.search('[0-9]+', doc).group())#t i e c b r
        Idf = round(math.log(totalCount/noDoc),3)
        #print (i, doc)
        if 't' in doc:
            s3 = doc.split('t')
            tId = int(re.search('[0-9]+', s3[1]).group())
            tTf = round(math.log(1 +tId),3)#tiecbr
            term_data_t = term_data_t +str(docId)+' '+str(round(tTf*Idf,3))+'|'
        if 'i' in doc:
            s4 = doc.split('i')
            iId = int(re.search('[0-9]+', s4[1]).group())
            iTf = round(math.log(1 +iId),3)
            term_data_i = term_data_i +str(docId)+' '+str(round(iTf*Idf,3))+'|'
        
        if 'e' in doc:
            s5 = doc.split('e')
            eId = int(re.search('[0-9]+', s5[1]).group())
            eTf = round(math.log(1 +eId),3)
            term_data_e = term_data_e +str(docId)+' '+str(round(eTf*Idf,3))+'|'
        
        if 'c' in doc:
            s6 = doc.split('c')
            cId = int(re.search('[0-9]+', s6[1]).group())
            cTf = round(math.log(1 +cId),3)
            term_data_c = term_data_c +str(docId)+' '+str(round(cTf*Idf,3))+'|'
        
        if 'b' in doc:
            s7 = doc.split('b')
            bId = int(re.search('[0-9]+', s7[1]).group())
            bTf = round(math.log(1 +bId),3)
            term_data_b = term_data_b+str(docId)+' '+str(round(bTf*Idf,3))+'|'
        
        if 'r' in doc:
            s8 = doc.split('r')
            rId = int(re.search('[0-9]+', s8[1]).group())
            rTf = round(math.log(1 +rId),3)
            term_data_r = term_data_r +str(docId)+' '+str(round(rTf*Idf,3))+'|'

        Tf = round(math.log(1 + 2*tId + iId + eId + 1.5*cId + bId + rId),3)
        term_data = term_data +str(docId) +' '+str(round(Tf*Idf,3))+'|'  
    
    if(term_data!=''):
        f_finalTFIDF.write(term+':'+term_data+'\n')
    if(term_data_t!=''):
        f_tTFIDF.write(term+':'+term_data_t+'\n')
    if(term_data_i!=''):
        f_iTFIDF.write(term+':'+term_data_i+'\n')
    if(term_data_e!=''):
        f_eTFIDF.write(term+':'+term_data_e+'\n')
    if(term_data_c!=''):
        f_cTFIDF.write(term+':'+term_data_c+'\n')
    if(term_data_b!=''):
        f_bTFIDF.write(term+':'+term_data_b+'\n')
    if(term_data_r!=''):
        f_rTFIDF.write(term+':'+term_data_r+'\n')
    
print("Total pages: {:,}".format(totalCount))
