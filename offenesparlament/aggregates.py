import logging
from collections import defaultdict

from offenesparlament.core import db
from pprint import pprint

log = logging.getLogger(__name__)

def db_function(name):
    data = {
            'week': {
                'sqlite': 'STRFTIME("%%Y-%%W", %s)',
                'postgresql': 'to_char(%s, \'YYYY-WW\')'
            }
        }
    return data[name][db.engine.url.drivername]

def _run_raw(query, *a, **kw):
    log.info(query)
    rp = db.engine.execute(query, *a, **kw)
    results = []
    while True: 
        row = rp.fetchone()
        if row is None:
            break
        results.append(dict(row.items()))
    return results

def result_tf(results, name, num):
    terms = defaultdict(int)
    for result in results:
        terms[result['name']] += result['num']
    total = sum(terms.values())
    return dict([(t, float(n)/total) for t, n in terms.items()])

def freq_diff(my, norm, limit):
    diffs = [((ctf-norm[t])*100.0, t) for t, ctf in my.items()]
    return sorted(diffs, reverse=True)[:limit]


# SELECT sw.name, COUNT(pos.id) AS num, STRFTIME("%Y-%W", pos.date) AS tspan FROM ablauf abl JOIN position pos ON pos.ablauf_id = abl.id JOIN schlagworte swe ON swe.ablauf_id = abl.id JOIN schlagwort sw ON swe.schlagwort_id = sw.id GROUP BY STRFTIME("%Y-%W", pos.date), sw.name ORDER BY num DESC;
def current_schlagworte(limit=15):
    func =  db_function('week') % 'pos.date'
    res = _run_raw("""SELECT sw.name, COUNT(pos.id) AS num, 
                        %s AS period
        FROM ablauf abl
            JOIN position pos ON pos.ablauf_id = abl.id
            JOIN schlagworte swe ON swe.ablauf_id = abl.id 
            JOIN schlagwort sw ON swe.schlagwort_id = sw.id 
        GROUP BY period, sw.name
        HAVING num > 1
        ORDER BY num DESC;""" % func)
    #pprint(res)
    term_freq = result_tf(res, 'name', 'num')
    #pprint(sorted(term_freq.items(), key=lambda (k,v): v))
    
    current = sorted(set([r['period'] for r in res]), reverse=True)[:2]
    currents = filter(lambda r: r['period'] in current, res)
    current_term_freq = result_tf(currents, 'name', 'num')
    current_top = freq_diff(current_term_freq, term_freq, limit)

    #fraktionen_top = {}
    #fraktionen = set([r['fraktion'] for r in res if r['fraktion']])
    #for fraktion in fraktionen:
    #    theirs = filter(lambda r: r['fraktion']==fraktion, currents)
    #    their_tf = result_tf(theirs, 'name', 'num')
    #    fraktionen_top[fraktion] = freq_diff(their_tf, current_term_freq, limit)
    
    return current_top #, fraktionen_top

def sachgebiete():
    func =  db_function('week') % 'pos.date'
    res = _run_raw("""SELECT abl.sachgebiet, COUNT(pos.id) AS num, %s AS period
        FROM ablauf abl 
            JOIN position pos ON pos.ablauf_id = abl.id
        GROUP BY period, abl.sachgebiet
        ORDER BY period ASC;""" % func)
    sachgebiete = set([r['sachgebiet'] for r in res if r['sachgebiet']])
    data = {'label': list(sachgebiete), 'values': []}
    by_period = defaultdict(lambda: defaultdict(int))
    for r in res:
        by_period[r['period']][r['sachgebiet']] = r['num']
    period = None
    for period, sg in sorted(by_period.items(), key=lambda (p,s): p):
        data['values'].append({
            'label': period.split("-")[-1],
            'values': [sg[s] for s in sachgebiete]
            })
    return data


# SELECT sw.name AS schlagwort, COUNT(pos.id) AS num FROM ablauf abl JOIN position pos ON pos.ablauf_id = abl.id JOIN schlagworte swe ON swe.ablauf_id = abl.id JOIN schlagwort sw ON swe.schlagwort_id = sw.id JOIN beitrag bei ON bei.position_id = pos.id WHERE bei.person_id = 138 GROUP BY sw.name ORDER BY num DESC;
def person_schlagworte(person, limit=10):
    return _run_raw("""SELECT sw.name AS schlagwort, COUNT(pos.id) AS num 
        FROM ablauf abl 
            JOIN position pos ON pos.ablauf_id = abl.id 
            JOIN schlagworte swe ON swe.ablauf_id = abl.id 
            JOIN schlagwort sw ON swe.schlagwort_id = sw.id 
            JOIN beitrag bei ON bei.position_id = pos.id 
        WHERE bei.person_id = ? 
        GROUP BY schlagwort 
        ORDER BY num DESC
        LIMIT ?;""", person.id, limit);
