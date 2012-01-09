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
def make_current_schlagwort():
    func =  db_function('week') % 'pos.date'
    db.engine.execute("""DELETE FROM current_schlagwort;""")
    db.engine.execute("""INSERT INTO current_schlagwort 
        SELECT sw.name AS schlagwort, COUNT(pos.id) AS num, 
                        %s AS period
        FROM ablauf abl
            JOIN position pos ON pos.ablauf_id = abl.id
            JOIN schlagworte swe ON swe.ablauf_id = abl.id 
            JOIN schlagwort sw ON swe.schlagwort_id = sw.id 
        GROUP BY period, schlagwort
        ORDER BY num DESC;""" % func)

def current_schlagworte(limit=15):
    res = _run_raw("""SELECT schlagwort AS name, num, period 
        FROM current_schlagwort 
        WHERE num > 1; """)
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

def make_period_sachgebiete():
    func =  db_function('week') % 'pos.date'
    db.engine.execute("""DELETE FROM period_sachgebiet;""")
    db.engine.execute("""INSERT INTO period_sachgebiet 
        SELECT abl.sachgebiet AS sachgebiet, COUNT(pos.id) AS num, %s AS period
        FROM ablauf abl 
            JOIN position pos ON pos.ablauf_id = abl.id
        GROUP BY period, sachgebiet
        ORDER BY period ASC;""" % func)

def sachgebiete():
    res = _run_raw("""SELECT sachgebiet, num, period 
            FROM period_sachgebiet; """)
    sachgebiete = set([r['sachgebiet'] for r in res if r['sachgebiet']])
    data = {'label': list(sachgebiete), 'values': []}
    by_period = defaultdict(lambda: defaultdict(int))
    for r in res:
        by_period[r['period']][r['sachgebiet']] = r['num']
    period = None
    periods = sorted(by_period.items(), key=lambda (p,s): p, reverse=True)[:20]
    for period, sg in periods[::-1]:
        sum_ = float(sum(sg[s] for s in sachgebiete))
        print sum_
        data['values'].append({
            #'label': period.split("-")[-1],
            'label': period,
            'values': [sg[s]/sum_ for s in sachgebiete],
            'count': [sg[s] for s in sachgebiete]
            })
        print data['values'][-1]
        print sum(data['values'][-1]['values'])
    return data


# SELECT sw.name AS schlagwort, COUNT(pos.id) AS num FROM ablauf abl JOIN position pos ON pos.ablauf_id = abl.id JOIN schlagworte swe ON swe.ablauf_id = abl.id JOIN schlagwort sw ON swe.schlagwort_id = sw.id JOIN beitrag bei ON bei.position_id = pos.id WHERE bei.person_id = 138 GROUP BY sw.name ORDER BY num DESC;
def make_person_schlagworte():
    db.engine.execute("""DELETE FROM person_schlagwort;""")
    db.engine.execute("""INSERT INTO person_schlagwort 
        SELECT bei.person_id AS person_id, 
            sw.name AS schlagwort, COUNT(pos.id) AS num 
        FROM ablauf abl 
            JOIN position pos ON pos.ablauf_id = abl.id 
            JOIN schlagworte swe ON swe.ablauf_id = abl.id 
            JOIN schlagwort sw ON swe.schlagwort_id = sw.id 
            JOIN beitrag bei ON bei.position_id = pos.id 
        GROUP BY person_id, schlagwort;""");

def person_schlagworte(person, limit=10):
    return _run_raw("""SELECT schlagwort, num 
        FROM person_schlagwort
        WHERE person_id = %s
        ORDER BY num DESC
        LIMIT %s;""" % (person.id, limit));
