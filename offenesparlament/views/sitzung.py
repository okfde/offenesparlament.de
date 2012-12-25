#coding: utf-8
from collections import defaultdict
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect

from offenesparlament.core import db
from offenesparlament.lib.searcher import SolrSearcher
from offenesparlament.lib.pager import Pager
from offenesparlament.lib.seo import render_sitemap
from offenesparlament.util import jsonify
from offenesparlament.model import Sitzung, Debatte, Rede, Zitat

sitzung = Blueprint('sitzung', __name__)


@sitzung.route("/plenum")
@sitzung.route("/plenum.<format>")
def index(format=None):
    searcher = SolrSearcher(Rede, request.args)
    searcher.add_facet('debatte.sitzung.titel')
    searcher.add_facet('zitate.person.name')
    searcher.sort('date', 'desc')
    pager = Pager(searcher, 'sitzung.index', request.args)
    if format == 'json':
        return jsonify({'results': pager})
    if searcher.has_query:
        return render_template('sitzung/reden.html',
                searcher=searcher, pager=pager,
                sitzungen=sitzungen)
    else:
        sitzungen = Sitzung.query.order_by(Sitzung.date.desc())
        return render_template('sitzung/index.html',
                searcher=searcher, pager=pager,
                sitzungen=sitzungen)


@sitzung.route("/plenum/<wahlperiode>/<nummer>")
@sitzung.route("/plenum/<wahlperiode>/<nummer>.<format>")
def view(wahlperiode, nummer, format=None):
    sitzung = Sitzung.query.filter_by(wahlperiode=wahlperiode,
                                      nummer=nummer).first()
    if sitzung is None:
        abort(404)
    searcher = SolrSearcher(Zitat, request.args)
    searcher.filter('sitzung.wahlperiode', sitzung.wahlperiode)
    searcher.filter('sitzung.nummer', sitzung.nummer)
    searcher.add_facet('debatte.titel')
    searcher.add_facet('redner')
    searcher.sort('sequenz', 'asc')
    pager = Pager(searcher, 'sitzung.view', request.args,
            wahlperiode=wahlperiode, nummer=nummer)
    pager.limit = 100
    if format == 'json':
        data = sitzung.to_dict()
        data['results'] = pager
        return jsonify(data)
    return render_template('sitzung/view.html',
            sitzung=sitzung, pager=pager, searcher=searcher)

@sitzung.route("/sitemap/plenum-<year>.xml")
def sitemap(year):
    items = []
    query = Debatte.query.join(Sitzung)
    query = query.filter(db.extract('year', Sitzung.date)==int(year))
    query = query.distinct(Debatte.id)
    for debatte in query:
        item = {'lastmod': debatte.updated_at,
                'loc': url_for('debatte.view', wahlperiode=debatte.sitzung.wahlperiode,
                               nummer=debatte.sitzung.nummer, debatte=debatte.id,
                               _external=True)}
        items.append(item)
    return render_sitemap(items, prio=0.9)

