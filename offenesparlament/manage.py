from flaskext.script import Manager
from webstore.client import URL as WebStore

from offenesparlament.core import app

manager = Manager(app)

@manager.command
def extract():
    """ Run the extract stage """
    db, _ = WebStore(app.config['STAGING_URL'])
    from offenesparlament.extract.xml import ausschuss
    ausschuss.load_index(db)
    from offenesparlament.extract.xml import news
    news.load_index(db)
    from offenesparlament.extract.xml import mdb
    mdb.load_index(db)
    from offenesparlament.extract import dip
    dip.load_dip(db)
    from offenesparlament.extracl import mediathek
    mediathek.load_sessions(db)

@manager.command
def longextract():
    """ Run the extract stage, including long-running tasks """
    pass

if __name__ == "__main__":
    manager.run()
