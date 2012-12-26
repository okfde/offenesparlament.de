#coding: utf-8
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect
from colander import Invalid

from offenesparlament.core import db
from offenesparlament.model import Abo
from offenesparlament.lib.abo import AboSchema, send_activation

abo = Blueprint('abo', __name__)


@abo.route("/abo", methods=['GET'])
def form():
    fields = {
        'query': request.args.get('query', ''),
        'email': request.args.get('email', ''),
        'include_activity': True,
        'include_speeches': True}
    return render_template('abo/form.html', fields=fields, errors={})


@abo.route("/abo", methods=['POST'])
def create():
    schema = AboSchema()
    try:
        data = dict(request.form.items())
        data = schema.deserialize(data)
        abo_ = Abo()
        abo_.email = data['email']
        abo_.query = data['query']
        abo_.include_speeches = data['include_speeches']
        abo_.include_activity = data['include_activity']
        db.session.add(abo_)
        db.session.commit()
        send_activation(abo_)
        flash(u"Das Themen-Abo wurde erfolgreich eingerichtet. Sie erhalten nun "
              u"eine Bestätigungs-EMail.", 'success')
        return redirect(url_for('index'))
    except Invalid, i:
        return render_template('abo/form.html', fields=request.form,
                errors=i.asdict())


@abo.route("/abo/activate/<key>")
def activate(key):
    abo = db.session.query(Abo).filter_by(activation_code=key).first()
    if abo is None:
        flash(u"Der Bestätigungscode ist ungültig oder das Abo bereits bestätigt.", 'warning')
    else:
        abo.activation_code = None
        db.session.commit()
        flash("Das Themen-Abo wurde erfolgreich eingerichtet.", 'success')
    return redirect(url_for('index'))


@abo.route("/abo/end/<id>")
def terminate(id):
    abo = db.session.query(Abo).filter_by(id=id)\
            .filter_by(email=request.args.get('email'))
    if abo is None:
        flash(u"Abo nicht gefunden.", 'warning')
    else:
        abo.activation_code = 'deleted ' + datetime.utcnow().isoformat()
        db.session.commit()
        flash("Das Themen-Abo wurde erfolgreich gekündigt.", 'success')
    return redirect(url_for('index'))

