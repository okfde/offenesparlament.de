# shut up useless SA warning:
import warnings; warnings.filterwarnings('ignore', 'Unicode type received non-unicode bind param value.')
import logging

logging.basicConfig(level=logging.NOTSET)

from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

from offenesparlament import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('PARLAMENT_SETTINGS', silent=True)

db = SQLAlchemy(app)


