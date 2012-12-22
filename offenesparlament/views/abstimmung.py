from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect

from offenesparlament.core import db
from offenesparlament.util import jsonify
from offenesparlament.model import Abstimmung, Stimme

abstimmung = Blueprint('abstimmung', __name__)


@abstimmung.route("/abstimmung/<id>")
@abstimmung.route("/abstimmung/<id>.<format>")
def view(id, format=None):
    abstimmung = Abstimmung.query.filter_by(id=id).first()
    if abstimmung is None:
        abort(404)
    ja = abstimmung.stimmen.filter(Stimme.entscheidung.like('%Ja%'))
    nein = abstimmung.stimmen.filter_by(entscheidung='Nein')
    enth = abstimmung.stimmen.filter_by(entscheidung='Enthaltung')
    na = abstimmung.stimmen.filter(Stimme.entscheidung.like('%nicht%'))

    return render_template('abstimmung/view.html',
        abstimmung=abstimmung, ja=ja, nein=nein, enth=enth, na=na)

