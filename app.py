from flask import Flask
from celery import Celery
from flask_pymongo import PyMongo

from flask import request
from flask import render_template
from flask import redirect

from bson.objectid import ObjectId
from bson import json_util

from datetime import datetime

import json

import choices
import helpers

app = Flask(__name__, static_url_path='/static')

# MongoDB Settings
app.config['MONGO_DBNAME'] = 'web_queries'
app.config['MONGO_USERNAME'] = 'db_admin'
app.config['MONGO_PASSWORD'] = 'dbpass'

mongo = PyMongo(app, config_prefix='MONGO')

# Celery Settings
app.config['CELERY_BROKER_URL'] = 'mongodb://db_admin:dbpass@127.0.0.1:27017/celery'
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
    return render_template('frontpage.html')


@app.route('/form/', methods=['GET'])
def form_home():
    """
    Not used
    :return string:
    """
    return 'Form Home'


@app.route('/form/motif/', methods=['GET'])
def motif_home():
    """
    Displays form motif create/select template
    :return template:
    """
    return render_template('/motif/index.html')


@app.route('/form/motif/create/', methods=['GET', 'POST'])
def motif_create():
    """
    Displays form motif creation template
    :return template:
    """
    if request.method == 'POST':
        # resend creation form if submitted motif string value length is less than 2
        if len(request.form['motif']) < 2:
            error = 'ERROR! Submitted motif not long enough! Please try again!'
            return render_template('/motif/create.html', error=error, motif_list=choices.AMINOACID_CHOICES)

        # resend creation form if motif already found in MongoDB motif collection
        if mongo.db.motif.find({'sequence_motif': request.form['motif']}).limit(1).count() > 0:
            error = 'ERROR! Motif already exists in database!'
            return render_template('/motif/create.html', error=error, motif_list=choices.AMINOACID_CHOICES)

        # create `motif` document as dict for insertion into MongoDB
        new_motif = {
            'sequence_motif': request.form['motif'],
            'datetime_added': datetime.utcnow(),
            'user': 'default',
        }
        mongo.db.motif.insert_one(new_motif)

        # redirect to form motif index upon `motif` document insertion
        return redirect('/form/motif/', code=302)
    else:
        return render_template('/motif/create.html', motif_list=choices.AMINOACID_CHOICES)


@app.route('/form/motif/select/', methods=['GET', 'POST'])
def motif_select():
    """
    Displays form motif selection template
    :return template:
    """
    if request.method == 'POST':
        # resend selection form to client if form `motif_list[]` multiple select field had no checked entities
        if len(request.form.getlist('motif_list[]')) == 0:
            error = 'ERROR! No motifs selected! Please select motifs to continue analysis!'
            query = mongo.db.motif.find({
                'user': 'default',
            }).sort([
                ('datetime_added', -1),
            ])
            return render_template('/motif/select.html', error=error, query=query)

        # convert form `motif_list[]` multiple select field checked values to bson.ObjectId type
        motif_list = helpers.convert_string_ids_to_bson_objectids(request.form.getlist('motif_list[]'))

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
        response = app.make_response(redirect('/form/sequences/', code=302))
        response.set_cookie('query_id', str(result.inserted_id))

        # redirects to form sequence index with `query_id` cookie in HTTP header
        return response
    else:
        # resend selection form to client with error message if no motifs saved in database
        if mongo.db.motif.find({'user': 'default'}).count() == 0:
            error = 'ERROR! No motifs saved in database! Please create motifs to continue analysis!'
            return render_template('/motif/select.html', error=error)

        # query database for `motif` documents & sort by `datetime_added` in descending order
        query = mongo.db.motif.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/motif/select.html', query=query)


@app.route('/form/sequences/', methods=['GET'])
def sequences_home():
    """
    Displays form sequence create/select template
    :return template:
    """
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies:
        return redirect('/form/motif/', code=302)

    return render_template('/sequences/index.html')


@app.route('/form/sequences/create/', methods=['GET', 'POST'])
def sequences_create():
    """
    Sequence creation form and database insertion.
    :return template:
    """
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies:
        return redirect('/form/motif/', code=302)

    if request.method == 'POST':
        # takes form inputs to try and create a sequence `collection` document for MongoDB insertion
        if request.form['collection_type'] == 'FASTA':
            # use Biopython SeqIO parser on form textarea `collection_textbox` to break string into Biopython SeqRecord
            # objects and returns an iterator
            collection = helpers.format_input(collection_text=request.form['collection_textbox'],
                                              file_type=request.form['collection_type'])

            # takes `collection` iterator and iterates over BioPython SeqRecords to create list of sequences as dicts
            collection = helpers.format_collection(collection=collection, file_type=request.form['collection_type'])

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
                return redirect('/form/sequences/', code=302)
            else:
                error = 'ERROR! Error parsing sequence list!'
                return render_template('/sequences/create.html', error=error, collection_types=choices.INPUT_TYPES)
        else:
            error = 'ERROR! Invalid collection type!'
            return render_template('/sequences/create.html', error=error, collection_types=choices.INPUT_TYPES)
    else:
        return render_template('/sequences/create.html', collection_types=choices.INPUT_TYPES)


@app.route('/form/sequences/select/', methods=['GET', 'POST'])
def sequences_select():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies:
        return redirect('/form/motif/', code=302)

    #
    if request.method == 'POST':
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
        return redirect('/form/options/', code=302)
    else:
        # query for sequence collections & sort by most recent `datetime_added`
        query = mongo.db.collection.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/sequences/select.html', query=query)


@app.route('/form/options/', methods=['GET', 'POST'])
def form_options():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies:
        return redirect('/form/motif/', code=302)

    #
    if request.method == 'POST':
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
    else:
        # get `query` document from stored cookie
        query = mongo.db.query.find_one({'_id': ObjectId(request.cookies.get('query_id'))})

        # render options template with `motifs` and `sequence_count`
        return render_template('/options/index.html', motifs=query['motifs_as_string'],
                               sequence_count=query['sequence_count'])


@app.route('/results/', methods=['GET'])
def results():
    # redirects to form motif index page if `query_id` cookie not set
    if 'query_id' not in request.cookies:
        return redirect('/form/motif/', code=302)

    # get `query` document from stored cookie
    query = mongo.db.query.find_one({'_id': ObjectId(request.cookies.get('query_id'))})

    # start analysis
    # SET TO DELAY WHEN RUNNING IN LINUX
    motif_analysis(query)

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
    query = mongo.db.query.find_one({'_id': ObjectId(request.cookies.get('query_id'))})
    return json.dumps({'query': query}, default=json_util.default)


@celery.task()
def motif_analysis(query):
    """
    Asynchronous query analysis via Celery
    :param query:
    :return:
    """
    # create shorter variables for motif frequency and frame size
    motif_frequency = query['motif_frequency']
    motif_frame_size = query['motif_frame_size']

    # create list with motifs
    motif_list = []
    for motif_id in query['motif_list']:
        motif_query = mongo.db.motif.find_one({'_id': motif_id})
        motif = motif_query['sequence_motif']
        motif_list.append(motif)

    # create list with collections
    collection_list = []
    for collection_id in query['collection_list']:
        collection_query = mongo.db.collection.find_one({'_id': collection_id})
        collection = collection_query['collection']
        collection_list.append(collection)

    # iterate through each sequence in each collection and do analysis
    result_list = []
    for collection in collection_list:
        collection_result_list = []
        for sequence in collection:
            analysis_result = helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size)
            sequence_result = {
                'sequence': sequence,
                'analysis': analysis_result,
            }
            collection_result_list.append(sequence_result)
        collection_result = {
            'result': collection_result_list,
        }
        result_list.append(collection_result)

    # update `query` document with results
    mongo.db.query.update({
        '_id': query['_id']
    }, {
        '$set': {
            'result': result_list,
            'done': True,
        }
    })


if __name__ == '__main__':
    app.run()
