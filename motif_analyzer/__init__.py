from flask import Flask
import os


# Flask Setup
app = Flask(__name__)
app.config.update(
    STATIC_FOLDER=os.path.join(os.getcwd(), 'static'),
    UPLOAD_FOLDER=os.path.join(os.getcwd(), 'uploads'),
    SECRET_KEY='ProjectSecretKey1337',
)

from motif_analyzer import views
