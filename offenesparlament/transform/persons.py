#coding: utf-8
import sys
import logging

from webstore.client import URL as WebStore

from offenesparlament.transform.text import url_slug

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

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
    return fp

def generate_person_long_names(db):
    log.info("Generating person fingerprints and slugs...")
    Person = db['person']
    for person in Person:
        long_name = make_long_name(person)
        log.debug(" -> %s" % long_name.strip())
        slug = url_slug(long_name)
        Person.writerow({'fingerprint': long_name,
                         'slug': slug,
                         '__id__': person['__id__']}, 
                         unique_columns=['__id__'])
    for fp in Person.distinct('fingerprint'):
        if fp['_count'] > 1:
            raise ValueError("Partial fingerprint: %s" % fp['fingerprint'])

    log.info("Updating 'rollen' to have fingerprints...")
    Rolle = db['rolle']
    for person in Person:
        if person['mdb_id']:
            Rolle.writerow({
                'mdb_id': person['mdb_id'],
                'fingerprint': person['fingerprint']
                }, unique_columns=['mdb_id'])
        elif person['source_url']:
            Rolle.writerow({
                'person_source_url': person['person_source_url'],
                'fingerprint': person['fingerprint']
                }, unique_columns=['person_source_url'])



if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    generate_person_long_names(db)

