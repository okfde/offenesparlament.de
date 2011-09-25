from offenesparlament.core import db

def _run_raw(query, *a, **kw):
    rp = db.engine.execute(query, *a, **kw)
    results = []
    while True: 
        row = rp.fetchone()
        if row is None:
            break
        results.append(dict(row.items()))
    return results

# SELECT sw.name, COUNT(pos.id) AS num, STRFTIME("%Y-%W", pos.date) AS tspan FROM ablauf abl JOIN position pos ON pos.ablauf_id = abl.id JOIN schlagworte swe ON swe.ablauf_id = abl.id JOIN schlagwort sw ON swe.schlagwort_id = sw.id GROUP BY STRFTIME("%Y-%W", pos.date), sw.name ORDER BY num DESC;


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
