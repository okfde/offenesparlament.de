import dataset
import re
from pprint import pprint
from collections import defaultdict
from unicodedata import normalize as ucnorm, category
from pattern.de import parse, split, parsetree
from pattern.search import search

def normalize(text):
    if not isinstance(text, unicode):
        text = unicode(text)
    decomposed = ucnorm('NFKD', text)
    filtered = []
    for char in decomposed:
        cat = category(char)
        if char in '\\*':
            filtered.append(char)
        elif char == "'" or cat.startswith('M') or cat.startswith('S'):
            continue
        elif cat.startswith('L') or cat.startswith('N'):
            filtered.append(char)
        else:
            #print [char]
            filtered.append(' ')
    text = u''.join(filtered)
    while '  ' in text:
        text = text.replace('  ', ' ')
    return ucnorm('NFKC', text).strip().lower()


def phrases():
    f  = open('./phrasen.csv', "rb") 
    lines = []
    for line in f:
        line = normalize(line.rstrip().decode('utf-8'))
        lines.append(line)
    f.close()
    return lines

def sentences(text):
    t = parsetree(text)
    sentences_that_match = []
    for sentence in t.sentences:
        nt = normalize(sentence.string)
        if(len(bull.findall(nt)) > 0):
            sentences_that_match.append(sentence.string)
    return sentences_that_match

phrases = phrases()
reg = '('+ '|'.join(phrases)+')'
bull = re.compile(reg)
words = re.compile('\w{2,}')

engine = dataset.connect('postgresql://localhost/plenary')
speech = engine['speech']
person = engine['person']

# phrases per party
# phrases per person
# phrases over time
# phrases by topic, per party
# best sentences
# bullshit score for person
# person, phrase, count, party
# split by sesson (histogram)
# trumpet
# which phrases get the biggest hit


bsfaktor = engine['phrases']
bsfaktor.delete()

for s in speech.find(type='speech', sitzung='210'):
    text = normalize(s['text'])
    number_found = len(bull.findall(text))
  
    sentences_that_match = sentences(s['text'])

    if(number_found > 0):
        # each sentence find matcher
        for sentence in sentences_that_match:
            matcher = filter(None, map(lambda phrase: phrase if len(re.compile(phrase).findall(sentence)) > 0 else '', phrases))
            
            person = person.find_one(fingerprint=s['fingerprint'])
            partei = person['partei'] if person else '' 

            bsfaktor.upsert({
                'phrase': sentence,
                'speech': s['text'],
                'match': matcher,
                'fingerprint': s['fingerprint'],
                'partei': partei,
                'sitzung': s['sitzung'],
                'phrase_word_count': len(words.findall(sentence)),
                'speech_word_count': len(words.findall(s['text']))
                }, ['phrase','fingerprint'])

print "saving some sentences"


# sentence | phrase | fingerprint | session | role
 

