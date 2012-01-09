# shut up useless SA warning:
import warnings; warnings.filterwarnings('ignore', 'Unicode type received non-unicode bind param value.')
import logging

logging.basicConfig(level=logging.NOTSET)

from solr import SolrConnection

from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.flatpages import FlatPages

from offenesparlament import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('PARLAMENT_SETTINGS', silent=True)

db = SQLAlchemy(app)
pages = FlatPages(app)

def solr():
    return SolrConnection(app.config['SOLR_URL'],
                http_user=app.config.get('SOLR_USER'),
                http_pass=app.config.get('SOLR_PASSWORD'))

def master_data():
    from webstore.client import URL as WebStore
    db, _ = WebStore(app.config['MASTER_URL'])
    return db

def etl_engine():
    from sqlaload import connect
    return connect(app.config['ETL_URL'])
