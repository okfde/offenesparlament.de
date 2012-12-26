#coding: utf-8
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect
from colander import Invalid

from offenesparlament.core import db
from offenesparlament.lib.searcher import SolrSearcher
from offenesparlament.lib.pager import Pager
from offenesparlament.lib.seo import render_sitemap
from offenesparlament.lib.feeds import make_feed
from offenesparlament.util import jsonify
from offenesparlament.data.aggregates import person_schlagworte
from offenesparlament.model import Abo, Person, Position, Debatte, Zitat

person = Blueprint('person', __name__)


@person.route("/person")
@person.route("/person.<format>")
def index(format=None):
    searcher = SolrSearcher(Person, request.args)
    searcher.add_facet('rollen.funktion')
    searcher.add_facet('rollen.fraktion')
    searcher.add_facet('berufsfeld')
    pager = Pager(searcher, 'person.index', request.args)
    if format == 'json':
        return jsonify({'results': pager})
    return render_template('person/index.html',
            searcher=searcher, pager=pager)


@person.route("/sitemap/person.xml")
def sitemap():
    persons = []
    for person in Person.query:
        data = {'lastmod': person.updated_at,
                'loc': url_for('person.view', slug=person.slug, _external=True)}
        persons.append(data)
    return render_sitemap(persons)


@person.route("/person/<slug>")
@person.route("/person/<slug>.<format>")
def view(slug, format=None):
    person = Person.query.filter_by(slug=slug).first()
    if person is None:
        abort(404)
    if format == 'json':
        return jsonify(person)
    searcher = SolrSearcher(Position, request.args)
    searcher.sort('date')
    searcher.filter('beitraege.person.id', str(person.id))
    pager = Pager(searcher, 'person.view', request.args, slug=person.slug)
    schlagworte = person_schlagworte(person)
    if format == 'json':
        data = person.to_dict()
        data['positionen'] = pager
        data['debatten'] = debatten
        return jsonify(data)
    elif format == 'rss':
        return make_feed(person.name, author=person.name,
            positionen=pager, debatten=debatten)
    return render_template('person/view.html',
            person=person, searcher=searcher,
            pager=pager, schlagworte=schlagworte)


@person.route("/person/<slug>/votes")
@person.route("/person/<slug>/votes.<format>")
def votes(slug, format=None):
    person = Person.query.filter_by(slug=slug).first()
    if person is None:
        abort(404)
    return render_template('person/votes.html',
            person=person)

