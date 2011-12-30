#coding: utf-8
import sys

import Levenshtein

import sqlaload as sl

from offenesparlament.transform.persons import make_person, make_long_name
from offenesparlament.core import etl_engine
from offenesparlament.core import master_data

CHOP_PARTS = [' ', ')', '(', '[', ']', u'Vizepräsidentin', u'Vizepräsident',
              u'ÜNDNIS']

def chop(txt):
    for part in CHOP_PARTS:
        txt = txt.replace(part, '')
    return txt

def levenshtein(a,b):
    return Levenshtein.distance(
            chop(a).lower(),
            chop(b).lower()
            )

def ensure_rolle(beitrag, fp, engine):
    rolle = {
        'fingerprint': fp,
        'ressort': beitrag.get('ressort'),
        'fraktion': beitrag.get('fraktion'),
        'funktion': beitrag.get('funktion')
        }
    Rolle = sl.get_table(engine, 'rolle')
    sl.upsert(engine, Rolle, rolle,
            unique=['fingerprint', 'funktion'])

def ask_user(beitrag, beitrag_print, matches, db):
    for i, (fp, dist) in enumerate(matches[:20]):
        m = " %s: %s (%s)" % (i, fp, dist)
        print m.encode('utf-8')
    sys.stdout.write("Enter choice or 'n' for new, 'x' for non-speaker [0]: ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not len(line.strip()):
        return matches[0][0]
    try:
        idx = int(line)
        ma, score = matches[idx]
        return ma
    except ValueError:
        line = line.lower().strip()
        if line == 'm':
            return ask_user(beitrag, beitrag_print, matches[20:], db)
        if line == 'x':
            raise ValueError()
        if line == 'n' and beitrag is not None:
            print "CREATING", beitrag_print.encode("utf-8")
            return make_person(beitrag, beitrag_print, db)

def match_beitrag(engine, master, beitrag, prints):
    beitrag_print = make_long_name(beitrag)
    print "Matching:", beitrag_print.encode('utf-8')
    matches = [(p, levenshtein(p, beitrag_print)) for p in prints]
    matches = sorted(matches, key=lambda (p,d): d)
    if not len(matches):
        # create new
        return make_person(beitrag, beitrag_print, db)
    first, dist = matches[0]
    if dist == 0:
        return first
    NameMatch = master['name_match']
    match = NameMatch.find_one(dirty=beitrag_print)
    if match is not None:
        Person = sl.get_table(engine, 'person')
        if sl.find_one(engine, Person, fingerprint=match.get('clean')) is None:
            return make_person(beitrag, match.get('clean'), engine)
        return match.get('clean')
    try:
        user_res = ask_user(beitrag, beitrag_print, matches, engine)
        NameMatch.writerow({'dirty': beitrag_print, 'clean': user_res})
        return user_res
    except ValueError: pass

def speaker_name_transform(name):
    cparts = name.split(',')
    if '(' in cparts[1]:
        cparts[1], pf = cparts[1].split(' (', 1)
        pf = pf.replace(')', '')
        cparts.append(pf)
    cparts[0], cparts[1] = cparts[1], cparts[0]
    fragment = " ".join(cparts)
    fragment.replace('(', '').replace(')', '')
    return fragment

_SPEAKER_CACHE = {}

def match_speaker(master, speaker, prints):
    if speaker not in _SPEAKER_CACHE:
        _SPEAKER_CACHE[speaker] = \
                _match_speaker(master, speaker, prints)
    return _SPEAKER_CACHE[speaker]

def _match_speaker(master, speaker, prints):
    print "Matching:", speaker.encode('utf-8')
    NonSpeaker = master['non_speaker']
    match = NonSpeaker.find_one(text=speaker)
    if match is not None:
        print "non-speaker!"
        raise ValueError()

    matches = [(p, levenshtein(p, speaker)) for p in prints]
    matches = sorted(matches, key=lambda (p,d): d)
    if not len(matches):
        return
    first, dist = matches[0]
    if dist == 0:
        return first
    NameMatch = master['name_match']
    match = NameMatch.find_one(dirty=speaker)
    if match is not None:
        return match.get('clean')
    try:
        user_res = ask_user(None, speaker, matches, None)
        if user_res is not None:
            NameMatch.writerow({'dirty': speaker, 'clean': user_res})
            return user_res
    except ValueError:
        NonSpeaker.writerow({'text': speaker}, unique_columns=['text'])

def match_speakers(engine, master, prints):
    Speech = sl.get_table(engine, 'mediathek')
    for i, speech in enumerate(sl.distinct(engine, Speech, 'speech_title')):
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if speech['speech_title'] is None:
            continue
        speaker = speaker_name_transform(speech['speech_title'])
        try:
            fp = match_speaker(master, speaker, prints)
        except ValueError:
            fp = None
        sl.upsert(engine, Speech, {'fingerprint': fp, 
                                   'speech_title': speech['speech_title']},
                    unique=['speech_title'])

QUERY = '''SELECT DISTINCT vorname, nachname, funktion, land, fraktion, 
           ressort, ort FROM beitrag;'''

def match_beitraege(engine, master, prints):
    Beitrag = sl.get_table(engine, 'beitrag')
    for i, beitrag in enumerate(sl.distinct(engine, Beitrag, 'vorname',
        'nachname', 'funktion', 'land', 'fraktion', 'ressort', 'ort')):
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        match = match_beitrag(engine, master, beitrag, prints)
        ensure_rolle(beitrag, match, engine)
        beitrag['fingerprint'] = match
        sl.upsert(engine, Beitrag, beitrag, unique=['vorname', 'nachname',
            'funktion', 'land', 'fraktion', 'ressort', 'ort'])

def make_prints(db):
    return [p.get('fingerprint') for p in db['person'].distinct('fingerprint') \
            if p.get('fingerprint')]


def match_persons(db, master):
    prints = make_prints(db)
    match_beitraege(db, master, prints)
    match_speakers(db, master, prints)

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    match_persons(engine, master_data())
