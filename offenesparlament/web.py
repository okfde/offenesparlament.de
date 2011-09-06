from flask import Flask, g, request, render_template, abort, flash, json
from flask import url_for, redirect, jsonify

from offenesparlament.core import app
from offenesparlament.model import Ablauf, Position
from offenesparlament.model import Person, Gremium
from offenesparlament.model import Sitzung, Zitat

from offenesparlament.pager import Pager
from offenesparlament.searcher import SolrSearcher

@app.route("/plenum/<wahlperiode>/<nummer>")
def sitzung(wahlperiode, nummer):
    sitzung = Sitzung.query.filter_by(wahlperiode=wahlperiode,
                                      nummer=nummer).first()
    if sitzung is None:
        abort(404)
    searcher = SolrSearcher(Zitat, request.args)
    searcher.filter('sitzung.wahlperiode', sitzung.wahlperiode)
    searcher.filter('sitzung.nummer', sitzung.nummer)
    searcher.add_facet('debatten_zitate.debatte.titel')
    searcher.add_facet('person.name')
    searcher.sort('sequenz', 'asc')
    pager = Pager(searcher, 'sitzung', request.args,
            wahlperiode=wahlperiode, nummer=nummer)
    pager.limit = 100
    return render_template('sitzung_view.html',
            sitzung=sitzung, pager=pager, searcher=searcher)

@app.route("/plenum")
def sitzungen():
    searcher = SolrSearcher(Sitzung, request.args)
    searcher.add_facet('wahlperiode')
    pager = Pager(searcher, 'sitzungen', request.args)
    return render_template('sitzung_search.html', 
            searcher=searcher, pager=pager)

@app.route("/position/<key>")
def position(key):
    position = Position.query.filter_by(key=key).first()
    if position is None:
        abort(404)
    return redirect(url_for('ablauf', 
        wahlperiode=position.ablauf.wahlperiode,
        key=position.ablauf.key) + '#' + position.key)

@app.route("/ablauf/<wahlperiode>/<key>")
def ablauf(wahlperiode, key):
    ablauf = Ablauf.query.filter_by(wahlperiode=wahlperiode,
                                    key=key).first()
    if ablauf is None:
        abort(404)
    return render_template('ablauf_view.html',
            ablauf=ablauf)

@app.route("/ablauf")
def ablaeufe():
    searcher = SolrSearcher(Ablauf, request.args)
    searcher.add_facet('initiative')
    searcher.add_facet('typ')
    searcher.add_facet('stand')
    searcher.add_facet('sachgebiet')
    searcher.add_facet('schlagworte')
    pager = Pager(searcher, 'ablaeufe', request.args)
    return render_template('ablauf_search.html', 
            searcher=searcher, pager=pager)

@app.route("/gremium")
def gremien():
    searcher = SolrSearcher(Gremium, request.args)
    pager = Pager(searcher, 'gremien', request.args)
    return render_template('gremium_search.html', 
            searcher=searcher, pager=pager)

@app.route("/gremium/<key>")
def gremium(key):
    gremium = Gremium.query.filter_by(key=key).first()
    if gremium is None:
        abort(404)
    searcher = SolrSearcher(Position, request.args)
    searcher.sort('date')
    #searcher.filter('beitraege.gremium.id', str(gremium.id))
    pager = Pager(searcher, 'gremium', request.args, key=key)
    return render_template('gremium_view.html',
            gremium=gremium, searcher=searcher, pager=pager)

@app.route("/person")
def persons():
    searcher = SolrSearcher(Person, request.args)
    searcher.add_facet('rollen.funktion')
    searcher.add_facet('rollen.fraktion')
    searcher.add_facet('berufsfeld')
    pager = Pager(searcher, 'persons', request.args)
    return render_template('person_search.html', 
            searcher=searcher, pager=pager)

@app.route("/person/<slug>")
def person(slug):
    person = Person.query.filter_by(slug=slug).first()
    if person is None:
        abort(404)
    searcher = SolrSearcher(Position, request.args)
    searcher.sort('date')
    searcher.filter('beitraege.person.id', str(person.id))
    pager = Pager(searcher, 'person', request.args, slug=slug)
    return render_template('person_view.html',
            person=person, searcher=searcher, pager=pager)

@app.route("/")
def index():
    return render_template('home.html')

if __name__ == '__main__':
    app.debug = True
    app.run(port=5006)
