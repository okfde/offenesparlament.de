import sys
import logging
from pprint import pprint
from collections import defaultdict

import sqlaload as sl

log = logging.getLogger(__name__)

import re

def drucksachen(text, wahlperiode=17):
    pat = r"(%s/\d{1,6}(\s*\(.{1,10}\))?)" % wahlperiode
    for drs, sufx in re.findall(pat, text):
        yield drs

def referenzen_index(engine):
    _referenzen = defaultdict(set)
    referenz_tbl = sl.get_table(engine, 'referenz')
    log.info("Building index of ablauf document references per session...")
    for ref in sl.all(engine, referenz_tbl):
        _referenzen[ref['ablauf_key']].add((ref['typ'], ref['nummer']))
    referenzen = defaultdict(set)
    for ablauf, refs in _referenzen.items():
        for typ, num in refs:
            if not '/' in num:
                continue
            if typ == 'plpr':
                wp, session= num.split('/')
                drs = [n for t, n in refs if t != 'plpr']
                if len(drs):
                    referenzen[(ablauf,wp,session)] = drs
    #pprint(dict(referenzen.items()))
    return referenzen

def item_index(engine):
    webtv_tbl = sl.get_table(engine, 'webtv')
    q = "SELECT s.text FROM speech s LEFT JOIN webtv_speech ws ON ws.wp::int = s.wahlperiode AND " \
        + "ws.session::int = s.sitzung AND ws.sequence = s.sequence " \
        + "WHERE ws.wp = '%(wp)s' AND ws.session = '%(session)s' AND ws.item_id = '%(item_id)s' AND s.type = 'chair' "
    items = {}
    log.info("Building index of drs mentions in speeches...")
    for item in sl.distinct(engine, webtv_tbl, 'wp', 'session', 'item_id'):
        _drs = set()
        for text in list(sl.query(engine, q % item)):
            _drs = _drs.union(drucksachen(text['text'], wahlperiode=item['wp']))
        if len(_drs):
            items[(item['wp'], item['session'], item['item_id'])] = _drs
    #pprint(items)
    return items

def merge_speeches(engine):
    # desired result: (position_id, debatte_id)
    referenzen = referenzen_index(engine)
    items = item_index(engine)
    
    log.info("Finding best matches.... ")
    matches = {}
    for (ablauf_id, rwp, rsession), rdrs in referenzen.items():
        for (iwp, isession, item_id), idrs in items.items():
            if iwp != rwp or rsession != isession:
                continue
            ints = len(idrs.intersection(rdrs))
            if ints == 0:
                continue
            k = (ablauf_id, rwp, rsession)
            if k in matches and matches[k][1] > ints:
                continue
            matches[k] = (item_id, ints)

    log.info("Saving position associations....")
    pos_tbl = sl.get_table(engine, 'position')
    for (ablauf_id, wp, session), (item_id, n) in matches.items():
        for pos in sl.find(engine, pos_tbl, ablauf_id="%s/%s" % (wp, ablauf_id)):
            if not pos['fundstelle_url']:
                continue
            if 'btp/%s/%s%03d.pdf' % (wp, wp, int(session)) in pos['fundstelle_url']:
                d = {'ablauf_id': pos['ablauf_id'], 
                     'hash': pos['hash'],
                     'debatte_wp': wp,
                     'debatte_session': session,
                     'debatte_item_id': item_id}
                sl.upsert(engine, pos_tbl, d, unique=['ablauf_id', 'hash'])

def merge_votes(engine):
    _referenzen = defaultdict(set)
    referenz_tbl = sl.get_table(engine, 'referenz')
    for ref in sl.all(engine, referenz_tbl):
        if ref['typ'] == 'drs':
            #print ref
            _referenzen[ref['nummer']].add(ref['ablauf_key'])
    mref = dict([(c, d) for c,d in _referenzen.items() if len(d)>1])
    print len(_referenzen), len(mref)



def merge(engine):
    #merge_speeches(engine)
    merge_votes(engine)
