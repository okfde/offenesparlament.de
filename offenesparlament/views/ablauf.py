#coding: utf-8
from collections import defaultdict
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect

from offenesparlament.core import db
from offenesparlament.lib.searcher import SolrSearcher
from offenesparlament.lib.pager import Pager
from offenesparlament.lib.seo import render_sitemap
from offenesparlament.util import jsonify
from offenesparlament.model import Ablauf, Position, Debatte, Zitat

ablauf = Blueprint('ablauf', __name__)


@ablauf.route("/sitemap/ablauf-<year>.xml")
def sitemap(year):
    items = []
    query = Ablauf.query.join(Position)
    query = query.filter(db.extract('year', Position.date)==int(year))
    query = query.distinct(Ablauf.id)
    for ablauf in query.yield_per(5000):
        item = {'lastmod': ablauf.updated_at, #ablauf.latest,
                'loc': url_for('ablauf.view', wahlperiode=ablauf.wahlperiode,
                               key=ablauf.key, _external=True)}
        items.append(item)
    return render_sitemap(items, prio=0.6)


@ablauf.route("/ablauf")
@ablauf.route("/ablauf.<format>")
def index(format=None):
    searcher = SolrSearcher(Ablauf, request.args)
    searcher.sort('date', 'desc')
    searcher.add_facet('initiative')
    searcher.add_facet('klasse')
    searcher.add_facet('stand')
    searcher.add_facet('sachgebiet')
    searcher.add_facet('schlagworte')
    pager = Pager(searcher, 'ablauf.index', request.args)
    if format == 'json':
        return jsonify({'results': pager})
    if not searcher.has_query_or_filter:
        query = Ablauf.query
        query = query.filter(Ablauf.zustimmungsbeduerftig != None)
        query = query.filter(Ablauf.abgeschlossen == False)

        ablaeufe = defaultdict(list)
        for ablauf in query:
            sg = ablauf.sachgebiet or "Sonstige"
            ablaeufe[sg].append(ablauf)
        return render_template('ablauf/index.html',
                searcher=searcher, pager=pager,
                ablaeufe=sorted(ablaeufe.items()))
    return render_template('ablauf/search.html',
            searcher=searcher, pager=pager)


@ablauf.route("/ablauf/<wahlperiode>/<key>")
@ablauf.route("/ablauf/<wahlperiode>/<key>.<format>")
def view(wahlperiode, key, format=None):
    ablauf = Ablauf.query.filter_by(wahlperiode=wahlperiode,
                                    key=key).first()
    if ablauf is None:
        abort(404)
    if format == 'json':
        return jsonify(ablauf)
    request.cache_key['modified'] = ablauf.updated_at
    referenzen = defaultdict(set)
    for ref in ablauf.referenzen:
        if ref.dokument.typ == 'plpr' and ref.dokument.hrsg == 'BT':
            continue
        if ref.seiten:
            referenzen[ref.dokument].add(ref.seiten)
        else:
            referenzen[ref.dokument] = referenzen[ref.dokument] or set()
    referenzen = sorted(referenzen.items(), key=lambda (r, s): r.name)
    return render_template('ablauf/view.html',
            ablauf=ablauf, referenzen=referenzen)

