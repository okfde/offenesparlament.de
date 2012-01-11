from flaskext.script import Manager
from webstore.client import URL as WebStore

from offenesparlament.core import app, master_data, etl_engine

manager = Manager(app)

@manager.command
def extract_base():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract.xml import ausschuss
    ausschuss.load_index(engine)
    from offenesparlament.extract.xml import news
    news.load_index(engine)
    from offenesparlament.extract.xml import mdb
    mdb.load_index(engine)

@manager.command
def extract_votes():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract import abstimmungen
    abstimmungen.load_index(engine)

@manager.command
def extract_media():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract import mediathek
    mediathek.load_sessions(engine)

@manager.command
def extract_docs():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract import dip
    dip.load_dip(engine)

@manager.command
def transform():
    """ Transform and clean up content """
    engine = etl_engine()
    master = master_data()
    from offenesparlament.transform import persons
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import ablaeufe
    ablaeufe.extend_ablaeufe(engine, master)
    from offenesparlament.transform import positions
    positions.extend_positions(engine)
    from offenesparlament.transform import namematch
    namematch.match_persons(engine, master)
    from offenesparlament.transform import abstimmungen
    abstimmungen.extend_abstimmungen(engine, master)
    #persons.generate_person_long_names(engine)
    from offenesparlament.transform import mediathek
    mediathek.extend_speeches(engine, master)
    from offenesparlament.transform import speechparser
    speechparser.load_transcripts(engine, master)
    mediathek.merge_speeches(engine, master)
    from offenesparlament.transform import speechmatch
    speechmatch.extend_speeches(engine, master)

@manager.command
def load():
    """ Load and index staging DB into production """
    engine = etl_engine()
    from offenesparlament.load import load
    load.load(engine)
    load.aggregate()
    from offenesparlament.load import index
    index.index()

@manager.command
def longextract():
    """ Run the extract stage, including long-running tasks """
    engine = etl_engine()
    from offenesparlament.extract import wahlkreise
    wahlkreise.load_wahlkreise(engine)

@manager.command
def notify():
    from offenesparlament.abo import notify
    from offenesparlament.web import app
    notify()

if __name__ == "__main__":
    manager.run()
