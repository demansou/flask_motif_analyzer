from flask import Flask
from celery import Celery
from flask_pymongo import PyMongo

from flask import flash, request, render_template, redirect, send_file

from werkzeug.utils import secure_filename

from bson.objectid import ObjectId
from bson import json_util

from datetime import datetime

import json
import os

import choices
import helpers

app = Flask(__name__, static_url_path='/static')

# Set Secret Key
app.config['SECRET_KEY'] = 'SuperDuperSecretKey64'

# File Upload Settings
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'fasta'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB Settings
app.config['MONGO_DBNAME'] = 'web_queries'
app.config['MONGO_USERNAME'] = 'db_admin'
app.config['MONGO_PASSWORD'] = 'dbpass'

mongo = PyMongo(app, config_prefix='MONGO')

# Celery Settings
app.config['CELERY_BROKER_URL'] = 'mongodb://db_admin:dbpass@127.0.0.1:27017/celery'
app.config['CELERY_IMPORTS'] = ("helpers.motif_analysis", "helpers.analyze_sequence",)
# ONLY NECESSARY FOR STORING RESULTS (RESULTS STORED IN WEB_QUERIES COLLECTION)
# app.config['CELERY_RESULT_BACKEND'] = 'mongodb://db_admin:dbpass@127.0.0.1:27017/celery_task_results'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/', methods=['GET'])
def app_home():
    """
    Displays app front page
    :return template:
    """
    query = mongo.db.motif.find({'user': 'default'}).sort([('datetime_added', -1)]).limit(3)
    response = app.make_response(render_template('frontpage.html', query=query))
    response.set_cookie('query_id', '')
    return response


@app.route('/motif/', methods=['GET', 'POST'])
def motif_select():
    """
    Displays form motif selection template
    :return template:
    """
    if request.method == 'GET':
        # query database for `motif` documents & sort by `datetime_added` in descending order
        default_motifs = mongo.db.motif.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/motif/select.html', default_motifs=default_motifs)

    ###############
    # POST METHOD #
    ###############

    # resend selection form to client if form `motif_list[]` multiple select field had no checked entities
    if len(request.form.getlist('motif_list[]')) == 0:
        flash('ERROR! No motifs selected! Please select motifs to continue analysis!')
        query = mongo.db.motif.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/motif/select.html', query=query)

    # convert form `motif_list[]` multiple select field checked values to bson.ObjectId type
    motif_list = helpers.convert_string_ids_to_bson_objectids(request.form.getlist('motif_list[]'))

    if motif_list is not False:
        # create string of `sequence_motif` values as comma separated values
        sequence_motif_list = []
        for motif_id in motif_list:
            motif_query = mongo.db.motif.find_one({'_id': motif_id})
            sequence_motif_list.append(motif_query['sequence_motif'])
        motifs_as_string = ', '.join(sequence_motif_list)

        # create `query` document as dict for insertion into MongoDB
        new_query = {
            'motif_list': motif_list,
            'motifs_as_string': motifs_as_string,
            'datetime_added': datetime.utcnow(),
            'user': 'default',
        }
        result = mongo.db.query.insert_one(new_query)

        # create client cookie `query_id` with MongoDB `query` document key
        response = app.make_response(redirect('/sequences/', code=302))
        response.set_cookie('query_id', str(result.inserted_id))

        # redirects to form sequence index with `query_id` cookie in HTTP header
        return response
    else:
        flash('ERROR! Invalid collection type!')
        query = mongo.db.motif.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/motif/select.html', query=query)


@app.route('/motif/create/', methods=['GET', 'POST'])
def motif_create():
    """
    Displays form motif creation template
    :return template:
    """
    if request.method == 'GET':
        return render_template('/motif/create.html', motif_list=choices.AMINOACID_CHOICES)

    ###############
    # POST METHOD #
    ###############

    # resend creation form if submitted motif string value length is less than 2
    if len(request.form['motif']) < 2:
        flash('ERROR! Submitted motif not long enough! Please try again!')
        return render_template('/motif/create.html', motif_list=choices.AMINOACID_CHOICES)

    # resend creation form if motif already found in MongoDB motif collection
    if mongo.db.motif.find({'sequence_motif': request.form['motif']}).limit(1).count() > 0:
        flash('ERROR! Motif already exists in database!')
        return render_template('/motif/create.html', motif_list=choices.AMINOACID_CHOICES)

    # create `motif` document as dict for insertion into MongoDB
    new_motif = {
        'sequence_motif': request.form['motif'],
        'datetime_added': datetime.utcnow(),
        'user': 'default',
    }
    mongo.db.motif.insert_one(new_motif)

    # redirect to form motif index upon `motif` document insertion
    return redirect('/motif/', code=302)


@app.route('/sequences/', methods=['GET', 'POST'])
def sequences_select():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies or len(request.cookies['query_id']) == 0:
        flash('Must select motifs to analyze before continuing to subsequent steps!')
        return redirect('/motif/', code=302)

    if request.method == 'GET':
        # query for sequence collections & sort by most recent `datetime_added`
        query = mongo.db.collection.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/sequences/select.html', query=query)

    ###############
    # POST METHOD #
    ###############

    # get list of collections
    collection_list = helpers.convert_string_ids_to_bson_objectids(request.form.getlist('collection_list[]'))

    # count sequences in collections
    sequence_count = 0
    for collection_id in collection_list:
        collection_query = mongo.db.collection.find_one({'_id': collection_id})
        sequence_count += len(collection_query['collection'])

    # update `query` document with collection ids and sequence count
    mongo.db.query.update({
        '_id': ObjectId(request.cookies.get('query_id')),
    }, {
        '$set': {
            'collection_list': collection_list,
            'sequence_count': sequence_count,
        }
    }, upsert=False)

    # after successful  update, redirect to form options page
    return redirect('/options/', code=302)


@app.route('/sequences/create/', methods=['GET', 'POST'])
def sequences_create():
    """
    Sequence creation form and database insertion.
    :return template:
    """
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies or len(request.cookies['query_id']) == 0:
        flash('Must select motifs to analyze before continuing to subsequent steps!')
        return redirect('/form/motif/', code=302)

    if request.method == 'GET':
        return render_template('/sequences/create.html', collection_types=choices.INPUT_TYPES)

    ###############
    # POST METHOD #
    ###############

    # takes form inputs to try and create a sequence `collection` document for MongoDB insertion
    if request.form['collection_type'] == 'FASTA':
        # takes textarea input and uses Biopython parsing function to create list of sequence dictionaries
        collection = helpers.format_textarea_text_fasta(input_text=request.form['collection_textbox'])

        # takes formatted `collection` and inserts `collection` document into MongoDB and redirects to form sequence
        # index OR returns error if invalid collection encountered
        if collection is not False:
            mongo.db.collection.insert_one({
                'collection_name': request.form['collection_name'],
                'collection_type': request.form['collection_type'],
                'collection': collection,
                'datetime_added': datetime.utcnow(),
                'user': 'default',
            })
            return redirect('/sequences/', code=302)
        else:
            flash('ERROR! Error adding sequences to database!')
            return render_template('/sequences/create.html', collection_types=choices.INPUT_TYPES)
    else:
        flash('ERROR! Invalid collection type!')
        return render_template('/sequences/create.html', error=error, collection_types=choices.INPUT_TYPES)


@app.route('/sequences/upload/', methods=['GET', 'POST'])
def sequences_upload():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies or len(request.cookies['query_id']) == 0:
        flash('Must select motifs before this step!')
        return redirect('/form/motif/', code=302)

    if request.method == 'GET':
        return render_template('/sequences/upload.html', collection_types=choices.INPUT_TYPES)

    ###############
    # POST METHOD #
    ###############

    # returns form page if file not found in request data
    if 'fasta_file' not in request.files:
        flash('ERROR! File not found in upload form! Please try again!')
        return redirect(request.url)

    file = request.files['fasta_file']

    # returns form page if filename is not present in request data
    # length of filename includes `.fasta` so at least 7 characters
    # for valid filename
    if len(file.filename) < 7:
        flash('ERROR! Invalid filename! Please try again!')
        return redirect(request.url)

    # creates collection document with data
    if file and helpers.is_allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(os.getcwd(), 'uploads', filename)
        file.save(file_path)

        # do stuff with file
        collection = helpers.format_file_fasta(file_path)
        if collection is not False:
            mongo.db.collection.insert_one({
                'collection_name': request.form['collection_name'],
                'collection_type': request.form['collection_type'],
                'collection': collection,
                'datetime_added': datetime.utcnow(),
                'user': 'default',
            })
            return redirect('/sequences/', code=302)

    # catchall error handler !!!REFINE!!!
    flash('ERROR! Not allowed filename or other error!')
    return redirect(request.url)


@app.route('/options/', methods=['GET', 'POST'])
def form_options():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies or len(request.cookies['query_id']) == 0:
        flash('Must select motifs to analyze before continuing to subsequent steps!')
        return redirect('/form/motif/', code=302)

    if request.method == 'GET':
        # get `query` document from stored cookie
        query = mongo.db.query.find_one({'_id': ObjectId(request.cookies.get('query_id'))})

        # render options template with `motifs` and `sequence_count`
        return render_template('/options/index.html', motifs=query['motifs_as_string'],
                               sequence_count=query['sequence_count'])

    ###############
    # POST METHOD #
    ###############

    # update query with `motif_frequency` and `motif_frame_size` analysis variables
    mongo.db.query.update({
        '_id': ObjectId(request.cookies.get('query_id')),
    }, {
        '$set': {
            'motif_frequency': int(request.form['motif_frequency']),
            'motif_frame_size': int(request.form['motif_frame_size']),
            'done': False,
        }
    }, upsert=False)

    # redirect to results page
    return redirect('/results/', code=302)


@app.route('/results/', methods=['GET'])
def results():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies or len(request.cookies['query_id']) == 0:
        flash('Must select motifs to analyze before continuing to subsequent steps!')
        return redirect('/form/motif/', code=302)

    # get `query` document from stored cookie
    query = mongo.db.query.find_one({'_id': ObjectId(request.cookies.get('query_id'))})

    # start analysis
    # SET TO DELAY WHEN RUNNING IN LINUX
    helpers.motif_analysis.delay(json.dumps(query, default=json_util.default))

    # render template with data for stats fields
    return render_template('/results/index.html', motifs=query['motifs_as_string'],
                           sequence_count=query['sequence_count'], motif_frequency=query['motif_frequency'],
                           motif_frame_size=query['motif_frame_size'])


@app.route('/status/', methods=['POST'])
def query_status():
    query = mongo.db.query.find_one({'_id': ObjectId(request.cookies.get('query_id'))})
    return json.dumps({'query_done': query['done']})


@app.route('/get_results/', methods=['POST'])
def get_results():
    query = mongo.db.result.find({
        '$and': [
            {'query_id': ObjectId(request.cookies.get('query_id'))},
            {'has_motif': True},
        ]
    })
    query_list = []
    for result in query:
        query_list.append(result)
    return json.dumps(query_list, default=json_util.default)


@app.route('/download_results/', methods=['GET'])
def get_file():
    file_name = ''.join([request.cookies.get('query_id'), '.csv'])
    file_path = os.path.join(os.getcwd(), 'downloads', file_name)
    return send_file(file_path, attachment_filename=file_name, as_attachment=True, mimetype='text/csv')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
