import re

from jinja2 import Markup

from offenesparlament.core import app
from offenesparlament.model import Dokument

DOK_PATTERN = re.compile(r"(\d{2,3}/\d{1,6}(\s*\(.{1,10}\))?)")

@app.template_filter()
def drslink(text, verbose=False):
    def r(m):
        num = m.group(1).replace(' ', '')
        dok = Dokument.query.filter_by(nummer=num).first()
        if dok is None:
            return m.group(1)
        link = "<a href='" + dok.link + "'>" + dok.nummer + "</a>"
        if verbose and dok.positionen.count() == 1:
            pos = dok.positionen.first()
            url = url_for('ablauf.view',
                    wahlperiode=pos.ablauf.wahlperiode,
                    key=pos.ablauf.key) + '#' + position.key
            link += " <span class='ablauf-ref'>(<a href='"+url+\
                    "'>"+pos.ablauf.titel+"</a>)</span>"
        return link
    text = DOK_PATTERN.sub(r, text)
    return Markup(text)

