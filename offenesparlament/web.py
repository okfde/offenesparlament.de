from flask import Flask, g, request, render_template, abort, flash, json
from flask import url_for, redirect, jsonify

from offenesparlament.core import app
from offenesparlament.model import Ablauf

from offenesparlament.pager import Pager
from offenesparlament.searcher import SolrSearcher

@app.route("/ablauf/<wahlperiode>/<key>")
def ablauf(wahlperiode, key):
    ablauf = Ablauf.query.filter_by(wahlperiode=wahlperiode,
                                    key=key).first()
    if ablauf is None:
        abort(404)
    return render_template('ablauf_view.html',
            ablauf=ablauf)

@app.route("/ablauf")
def search():
    searcher = SolrSearcher(Ablauf, request.args)
    searcher.add_facet('initiative')
    searcher.add_facet('typ')
    searcher.add_facet('stand')
    searcher.add_facet('sachgebiet')
    searcher.add_facet('schlagworte')
    pager = Pager(searcher, 'search', request.args)
    return render_template('ablauf_search.html', 
            searcher=searcher, pager=pager)

@app.route("/")
def index():
    return render_template('home.html')

if __name__ == '__main__':
    app.debug = True
    app.run(port=5006)
