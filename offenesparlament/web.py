from flask import Flask, g, request, render_template, abort, flash, json
from flask import url_for, redirect, jsonify

from offenesparlament.core import app
from offenesparlament.model import Ablauf

@app.route("/ablauf/<wahlperiode>/<key>")
def ablauf(wahlperiode, key):
    ablauf = Ablauf.query.filter_by(wahlperiode=wahlperiode,
                                    key=key).first()
    if ablauf is None:
        abort(404)
    return render_template('ablauf.html',
            ablauf=ablauf)

@app.route("/")
def index():
    return render_template('home.html')

if __name__ == '__main__':
    app.debug = True
    app.run(port=5006)
