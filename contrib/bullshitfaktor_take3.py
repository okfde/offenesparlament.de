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
people = {}

bsfaktor = engine['phrases']
bsfaktor.delete()

splitter = re.compile(r'[\.\?!]', re.M)

engine.begin()
for s in speech.find(type='speech'):
    #text = parsetree(s['text'])

    #for count,item in enumerate(text.sentences):
    for count, sentence in enumerate(splitter.split(s['text'])):
        #sentence = item.string
        normalised_sentence = normalize(sentence)

        matches = bull.findall(normalised_sentence)
        for match in matches:
            # print sentence.string
            if s['fingerprint'] not in people.keys():
                people[s['fingerprint']] = person.find_one(fingerprint=s['fingerprint'])
            
            p = people[s['fingerprint']]

            # p = person.find_one(fingerprint=s['fingerprint'])
            partei = p['partei'] if p else ''
            print [match, sentence]

            bsfaktor.upsert({
                'sentence': sentence,
                'sentence_number': count,
                'phrase': match,
                'fingerprint': s['fingerprint'],
                'partei': partei,
                'sequence': s['sequence'],
                'sitzung': s['sitzung'],
                'sentence_word_count': len(words.findall(sentence))
                }, ['sitzung','sequence','sentence_number'])

engine.commit()

print "saving some sentences"


# sentence | phrase | fingerprint | session | role
 

