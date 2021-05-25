import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import math
import nltk
from nltk import tokenize
from operator import itemgetter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

PATTERN_S = '<pattern>'
PATTERN_E = '</pattern>\n'
CATEGORY_S = '<category>\n'
CATOGORY_E = '</category>\n'
TEMPLATE_S = '<template>\n'
TEMPLATE_E = '</template>\n'
RANDOM_S = '<random>\n'
RANDOM_E = '</random>\n'
SRAI_S = '<srai>'
SRAI_E = '</srai>'
LI_S = '<li>'
LI_E = '</li>\n'
AIML_S = '<aiml>\n'
AIML_E = '</aiml>\n'

def get_urls():
    urls = []

    response = requests.get('https://en.wikipedia.org/wiki/Category:Chatbots')

    soup = BeautifulSoup(response.content, 'html.parser')

    data = soup.findAll('div', attrs={'class':'mw-category'})
    base = 'https://en.wikipedia.org'

    for div in data:
        links = div.findAll('a')
        for a in links:
            urls.append(base + a['href'])

    file = open('urls.txt', 'w')

    for url in urls:
        file.write(url)
        file.write('\n')
    file.close()


def check_sent(word, sentences): 
    final = [all([w in x for w in word]) for x in sentences] 
    sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
    return int(len(sent_len))


# get top k keywords
def keywordExtraction(content, k = 5):
    stop_words = set(stopwords.words('english'))
    words = re.sub(r'[^\w\s]', '', content).split()

    words_len = len(words)
    
    sentences = tokenize.sent_tokenize(content)
    sentences_len = len(sentences)

    # get tf score
    tf_score = {}
    for word in words:
        if not word.isnumeric() and word.lower() not in stop_words:
            if word in tf_score:
                tf_score[word] += 1
            else:
                tf_score[word] = 1

    tf_score.update((x, y/int(words_len)) for x, y in tf_score.items())

    # get idf score
    idf_score = {}
    for word in words:
        if not word.isnumeric() and word.lower() not in stop_words:
            idf_score[word] = check_sent(word, sentences)
        else:
            idf_score[word] = 1

    idf_score.update((x, math.log(int(sentences_len)/y)) for x, y in idf_score.items())

    tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}

    return sorted(tf_idf_score, key=tf_idf_score.get, reverse=True)[:k]


def getInfo():

    file = open('urls.txt', 'r')

    urls = file.readlines()

    # to store a list of key words and list of contents
    knowledge = []

    for url in urls:
  
        source = urlopen(url).read()
        soup = BeautifulSoup(source,'lxml')

        title = soup.find(id='firstHeading').text
        content = ''
        for p in soup.find_all('p'):
            content += p.text

        content = content.replace("&", "and")
        content = re.sub(r"\[.*?\]+", '', content)

        '''
        keywords =[x.upper() for x in keywordExtraction(content)]
        if title.upper() not in keywords:
            keywords.append(title.upper())
        '''
        keywords = [title.upper()]

        content = content.strip().split('\n')
        content = [x for x in content if len(x) != 0]
        content = [x for x in content if x[-1] == '.' or x[-1] == '?']

        knowledge.append((keywords, content))
        
    # write to aiml file
    writeHeader("knowledge_s.aiml")
    writeCategory("knowledge_s.aiml", knowledge)
    writeEnding("knowledge_s.aiml")


def writeCategory(filename: str, knowledge: list):
    file = open(filename, 'a', encoding='utf-8')
    for (keywords, content) in knowledge:
        # write main body
        key = keywords[0]
        file.write(CATEGORY_S)
        file.write(PATTERN_S + key + PATTERN_E)
        file.write(TEMPLATE_S)
        file.write(RANDOM_S)
        for paragraph in content:
            file.write(LI_S + paragraph + LI_E)
        file.write(RANDOM_E)
        file.write(TEMPLATE_E)
        file.write(CATOGORY_E)

        # write synonyms
        for keyword in keywords:
            combos = ['_ ' + keyword, keyword + ' *', '_ ' + keyword + ' *', keyword]
            for combo in combos:
                if combo == key:
                    continue
                file.write(CATEGORY_S)
                file.write(PATTERN_S + combo + PATTERN_E)
                file.write(TEMPLATE_S)
                file.write(SRAI_S + key + SRAI_E)
                file.write(TEMPLATE_E)
                file.write(CATOGORY_E)

    file.close()


def writeHeader(filename):
    file = open(filename, 'a', encoding='utf-8')
    file.write('<?xml version = "1.0" encoding = "UTF-8"?>\n')
    file.write(AIML_S)
    file.close()


def writeEnding(filename):
    file = open(filename, 'a', encoding='utf-8')
    file.write(AIML_E)
    file.close()


getInfo()