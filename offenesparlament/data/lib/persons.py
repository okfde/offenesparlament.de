#coding: utf-8
import sqlaload as sl

from offenesparlament.data.lib.text import url_slug
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference

def make_long_name(data):
    pg = lambda n: data.get(n) if data.get(n) and data.get(n) != 'None' else ''
    # dept. names are long and skew levenshtein otherwise:
    ressort = "".join([x[0] for x in pg('ressort').split(' ') if len(x)])
    fraktion = pg('fraktion').replace(u"BÜNDNIS ", "B")
    return "%s %s %s %s %s" % (pg('titel'),
            pg('vorname'), pg('nachname'), pg('ort'),
            fraktion or ressort)

def make_person(engine, beitrag, fp, source_url):
    try:
        fp = resolve_person(fp)
        person = {
            'fingerprint': fp,
            'slug': url_slug(fp),
            'source_url': source_url,
            'vorname': beitrag['vorname'],
            'nachname': beitrag['nachname'],
            'ort': beitrag.get('ort'),
            'ressort': beitrag.get('ressort'),
            'land': beitrag.get('land'),
            'fraktion': beitrag.get('fraktion')
        }
        sl.upsert(engine, sl.get_table(engine, 'person'), person,
                  unique=['fingerprint'])
    except BadReference: pass
    return fp

