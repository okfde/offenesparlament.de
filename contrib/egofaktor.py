import dataset
import re
from collections import defaultdict
from unicodedata import normalize as ucnorm, category

egos = re.compile(r'\b(ich|mir|mein|meiner|meines|mich|meines)\b', re.U)
words = re.compile('\w{2,}')

engine = dataset.connect('postgresql://localhost/parlament_etl')
speech = engine['speech']

def normalize(text):
    if not isinstance(text, unicode):
        text = unicode(text)
    decomposed = ucnorm('NFKD', text)
    filtered = []
    for char in decomposed:
        cat = category(char)
        if char == "'" or cat.startswith('M') or cat.startswith('S'):
            continue
        elif cat.startswith('L') or cat.startswith('N'):
            filtered.append(char)
        else:
            filtered.append(' ')
    text = u''.join(filtered)
    while '  ' in text:
        text = text.replace('  ', ' ')
    return ucnorm('NFKC', text).strip().lower()


num_egos = defaultdict(int)
num_words = defaultdict(int)

for s in speech.find(type='speech'):
    if s['sitzung'] < 190 or s['in_writing']:
        continue
    text = normalize(s['text'])
    num_egos[s['fingerprint']] += len(egos.findall(text))
    num_words[s['fingerprint']] += len(words.findall(text))
    #print [num_egos, num_words]

print "Done, saving..."
egofaktor = engine['egos']
egofaktor.delete()
for fp in num_egos.keys():
    pers = engine['person'].find_one(fingerprint=fp) or {}
    partei = None
    if 'partei' in pers:
        partei = pers['partei']
    egofaktor.upsert({
        'fingerprint': fp,
        'partei': partei,
        'egos': num_egos[fp],
        'words': num_words[fp]
        }, ['fingerprint'])

