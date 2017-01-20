from flask import Flask
from flask_pymongo import PyMongo

from flask import request
from flask import render_template

from datetime import datetime

import choices

app = Flask(__name__, static_url_path='/static')

# MongoDB Settings
app.config['MONGO_DBNAME'] = 'web_queries'
app.config['MONGO_USERNAME'] = 'db_admin'
app.config['MONGO_PASSWORD'] = 'dbpass'

mongo = PyMongo(app, config_prefix='MONGO')


@app.route('/', methods=['GET'])
def app_home():
    return render_template('frontpage.html')


@app.route('/form/', methods=['GET'])
def form_home():
    return 'Form Home'


@app.route('/form/motif/', methods=['GET'])
def motif_home():
    return render_template('/motif/index.html')


@app.route('/form/motif/create/', methods=['GET', 'POST'])
def motif_create():
    if request.method == 'POST':
        # move document format to object later
        new_motif = {
            'sequence_motif': request.form['motif'],
            'datetime_added': datetime.utcnow(),
            'user': 'default',
        }
        if mongo.db.motif.find({'sequence_motif': request.form['motif']}).limit(1).count() < 1:
            mongo.db.motif.insert_one(new_motif)
            return render_template('/motif/index.html', success=True, motif=request.form['motif'])
        else:
            return render_template('/motif/index.html', success=False, motif=request.form['motif'])
    else:
        return render_template('/motif/create.html', motif_list=choices.AMINOACID_CHOICES)


@app.route('/form/motif/select/', methods=['GET', 'POST'])
def motif_select():
    if request.method == 'POST':
        return 'Form Motif Select Received!'
    else:
        query = mongo.db.motif.find({'user': 'default'})
        return render_template('/motif/select.html', query=query)


@app.route('/form/sequences/', methods=['GET'])
def sequences_home():
    return 'Form Sequences Home'


@app.route('/form/sequences/create', methods=['GET', 'POST'])
def sequences_create():
    if request.method == 'POST':
        return 'Form Sequences Create Received!'
    else:
        return 'Form Sequences Create'


@app.route('/form/sequences/select', methods=['GET', 'POST'])
def sequences_select():
    if request.method == 'POST':
        return 'Form Sequences Select Received!'
    else:
        return 'Form Sequences Select'


if __name__ == '__main__':
    app.run()
