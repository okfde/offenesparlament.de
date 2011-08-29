#coding: utf-8
import sys

import Levenshtein

from webstore.client import URL as WebStore

from offenesparlament.transform.persons import make_person, make_long_name

def levenshtein(a,b):
    return Levenshtein.distance(
            a.replace(' ', '').lower(), 
            b.replace(' ', '').lower()
            )

def ensure_rolle(beitrag, fp, db):
    rolle = {
        'fingerprint': fp,
        'ressort': beitrag.get('ressort'),
        'fraktion': beitrag.get('fraktion'),
        'funktion': beitrag.get('funktion')
        }
    db['rolle'].writerow(rolle,
            unique_columns=['fingerprint', 'funktion'])

def ask_user(beitrag, beitrag_print, matches, db):
    for i, (fp, dist) in enumerate(matches):
        m = " %s: %s (%s)" % (i, fp, dist)
        print m.encode('utf-8')
    sys.stdout.write("Enter choice number or 'n' for new [0]: ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    print line
    if not len(line.strip()):
        return matches[0][0]
    try:
        idx = int(line)
        ma, score = matches[idx]
        return ma
    except ValueError:
        return make_person(beitrag, beitrag_print, db)

def match_beitrag(db, beitrag, prints):
    beitrag_print = make_long_name(beitrag)
    print "Matching:", beitrag_print.encode('utf-8')
    matches = [(p, levenshtein(p, beitrag_print)) for p in prints]
    matches = sorted(matches, key=lambda (p,d): d)[:5]
    if not len(matches):
        # create new
        return make_person(beitrag, beitrag_print, db)
    first, dist = matches[0]
    if dist == 0:
        return first
    NameMatch = db['name_match']
    match = NameMatch.find_one(dirty=beitrag_print)
    if match is not None:
        Person = db['person']
        if Person.find_one(fingerprint=match.get('clean')) is None:
            return make_person(beitrag, match.get('clean'), db)
        return match.get('clean')
    user_res = ask_user(beitrag, beitrag_print, matches, db)
    NameMatch.writerow({'dirty': beitrag_print, 'clean': user_res})
    return user_res

def match_persons(db):
    prints = [p.get('fingerprint') for p in db['person'].distinct('fingerprint')]
    Beitrag = db['beitrag']
    for beitrag in Beitrag:
        match = match_beitrag(db, beitrag, prints)
        ensure_rolle(beitrag, match, db)
        beitrag['fingerprint'] = match
        Beitrag.writerow(beitrag, unique_columns=['__id__'])

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    match_persons(db)
