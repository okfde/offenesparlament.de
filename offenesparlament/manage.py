from flaskext.script import Manager
from webstore.client import URL as WebStore

from offenesparlament.core import app, master_data

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
    from offenesparlament.extract import mediathek
    mediathek.load_sessions(db)
    from offenesparlament.extract import abstimmungen
    abstimmungen.load_index(db)

@manager.command
def transform():
    """ Transform and clean up content """
    db, _ = WebStore(app.config['STAGING_URL'])
    master = master_data()
    from offenesparlament.transform import persons
    persons.generate_person_long_names(db)
    from offenesparlament.transform import ablaeufe
    ablaeufe.extend_ablaeufe(db, master)
    from offenesparlament.transform import positions
    positions.extend_positions(db)
    from offenesparlament.transform import namematch
    namematch.match_persons(db, master)
    from offenesparlament.transform import abstimmungen
    abstimmungen.extend_abstimmungen(db, master)
    #persons.generate_person_long_names(db)
    from offenesparlament.transform import mediathek
    mediathek.extend_speeches(db, master)
    from offenesparlament.transform import speechparser
    speechparser.load_transcripts(db, master)
    mediathek.merge_speeches(db, master)
    from offenesparlament.transform import speechmatch
    speechmatch.extend_speeches(db, master)

@manager.command
def load():
    """ Load and index staging DB into production """
    db, _ = WebStore(app.config['STAGING_URL'])
    from offenesparlament.load import load
    load.load(db)
    from offenesparlament.load import index
    index.index(db)

@manager.command
def longextract():
    """ Run the extract stage, including long-running tasks """
    pass

if __name__ == "__main__":
    manager.run()
