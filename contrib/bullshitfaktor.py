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

#[{sentence:"SDf", taggedSentence:'sdf'}]
reg = '('+ '|'.join(phrases())+')'
bull = re.compile(reg)
words = re.compile('\w{2,}')

engine = dataset.connect('postgresql://localhost/plenary')
speech = engine['speech']
person = engine['person']

num_phrases = defaultdict(int)
num_words = defaultdict(int)
num_phrases_by_sitting = defaultdict(int)
num_words_by_sitting = defaultdict(int)
phrases_by_speaker = defaultdict(list)
phrases_by_sitting = defaultdict(list)
# phrases per party
# phrases per person
# phrases over time
# phrases by topic, per party
# best ifs
# bullshit score for person
# person, phrase, count, party
# split by sesson (histogram)
# trumpet
# which phrases get the biggest hit


for s in speech.find(type='speech'):
    #if s['sitzung'] < 190 or s['in_writing']:
    #    continue
    #print [s]
    text = normalize(s['text'])
    number_found = len(bull.findall(text))
    #print number_found
    if(number_found > 0):
        word_count = len(words.findall(text))
        # if by person
        num_phrases[s['fingerprint']] += number_found
        num_words[s['fingerprint']] += word_count

        sentences_that_match = sentences(s['text'])
  
        phrases_by_speaker[s['fingerprint']] = phrases_by_speaker[s['fingerprint']] + sentences_that_match
        
        #print sentences_that_match
        # Sentences that match by sitting
        num_words_by_sitting[s['sitzung']] += word_count
        num_phrases_by_sitting[s['sitzung']] += number_found
        phrases_by_sitting[s['sitzung']] = phrases_by_sitting[s['sitzung']] + sentences_that_match
    # phrases_by_speaker[s['fingerprint']]
            #sentences_in_sitting = extractSentence(s['text'])
        #print phrases_by_sitting[s['sitzung']]
    # print(len(bull.findall(text)))

# pprint(dict(phrases_by_sitting))

print "saving some phrases by speaker"
bsfaktor = engine['phrases_by_speaker']
bsfaktor.delete()
for fp in num_phrases.keys():
    partei = ''
    
    print fp
    person = person.find(fingerprint=fp)
    partei = person['partei'] if person else '' 
    print partei
    bsfaktor.upsert({
        'fingerprint': fp,
        'partei': partei,
        'phrases': num_phrases[fp],
        'words': num_words[fp],
        'sentences': phrases_by_speaker[fp]
        }, ['fingerprint'])

print "saving some phrases by sitting"
bs = engine['phrases_by_sitting']
bs.delete()
for siz in num_phrases_by_sitting.keys():
    bs.upsert({
        'sitzung': siz,
        'sentences': phrases_by_sitting[siz],
        'phrases': num_phrases_by_sitting[siz]
        }, ['sitzung'])
print "saving some sentences"


# sentence | phrase | fingerprint | session | role
 

