#coding: utf-8
import sys
import hashlib
import string

import Levenshtein

from webstore.client import URL as WebStore

def levenshtein(a,b):
    return Levenshtein.distance(
            a.replace(' ', '').lower(), 
            b.replace(' ', '').lower()
            )

def make_long_name(data):
    pg = lambda n: data.get(n) if data.get(n) and data.get(n) != 'None' else ''
    # dept. names are long and skew levenshtein otherwise:
    #ressort = hashlib.sha1(pg('ressort').encode('utf-8')).hexdigest()[:5]
    ressort = "".join([x[0] for x in pg('ressort').split(' ') if len(x)])
    fraktion = pg('fraktion').replace(u"BÜNDNIS ", "B")
    return "%s %s %s %s %s" % (pg('titel'), 
            pg('vorname'), pg('nachname'), pg('ort'), 
            fraktion or ressort)

def make_person(beitrag, fp, db):
    person = {
        'fingerprint': fp,
        'vorname': beitrag['vorname'],
        'nachname': beitrag['nachname'],
        'ort': beitrag.get('ort'),
        'ressort': beitrag.get('ressort'),
        'land': beitrag.get('land'),
        'fraktion': beitrag.get('fraktion')
    }
    db['person'].writerow(person,
            unique_columns=['fingerprint'])
    rolle = {
        'fingerprint': fp,
        'ressort': beitrag.get('ressort'),
        'fraktion': beitrag.get('fraktion'),
        'funktion': beitrag.get('funktion')
        }
    db['rolle'].writerow(rolle,
            unique_columns=['fingerprint', 'funktion'])
    return fp



def generate_person_long_names(db):
    Person = db['person']
    prints = set()
    for person in Person:
        long_name = make_long_name(person)
        print long_name.encode("utf-8").strip()
        prints.add(long_name)
        Person.writerow({'fingerprint': long_name, 
                         '__id__': person['__id__']}, 
                         unique_columns=['__id__'])
    for fp in Person.distinct('fingerprint'):
        if fp['_count'] > 1:
            raise ValueError("Partial fingerprint: %s" % fp['fingerprint'])

    print "Updating 'rollen' to have fingerprints...."
    Rolle = db['rolle']
    for person in Person:
        if 'mdb_id' not in person:
            continue
        Rolle.writerow({
            'mdb_id': person['mdb_id'],
            'fingerprint': person['fingerprint']
            }, unique_columns=['mdb_id'])
    return prints

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

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    prints = generate_person_long_names(db)
    #prints = [p.get('fingerprint') for p in db['person'].distinct('fingerprint')]
    for beitrag in db['beitrag']:
        match = match_beitrag(db, beitrag, prints)


