

# SELECT sw.name, COUNT(pos.id) AS num, STRFTIME("%Y-%W", pos.date) AS tspan FROM ablauf abl JOIN position pos ON pos.ablauf_id = abl.id JOIN schlagworte swe ON swe.ablauf_id = abl.id JOIN schlagwort sw ON swe.schlagwort_id = sw.id GROUP BY STRFTIME("%Y-%W", pos.date), sw.name ORDER BY num DESC;
