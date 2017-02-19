from __future__ import absolute_import
from flask import Flask
from flask_pymongo import PyMongo
import os

from .celery_config import make_celery

# Flask Setup
app = Flask(__name__)
app.config.update(
    STATIC_FOLDER=os.path.join(os.getcwd(), 'static'),
    UPLOAD_FOLDER=os.path.join(os.getcwd(), 'uploads'),
    SECRET_KEY='ProjectSecretKey1337',
    MONGO_DBNAME=app.name,
    MONGO_USERNAME='db_admin',
    MONGO_PASSWORD='dbpass',
    CELERY_BROKER_URL='mongodb://db_admin:dbpass@127.0.0.1:27017/celery'
)

# MongoDB Setup
mongo = PyMongo(app, config_prefix='MONGO')

# Celery Setup
celery = make_celery(app)

from motif_analyzer import views
from motif_analyzer import tasks
