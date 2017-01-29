from flask import Flask
from flask_pymongo import PyMongo

from flask import request
from flask import render_template
from flask import redirect

from datetime import datetime


import choices
import helpers

app = Flask(__name__, static_url_path='/static')

# MongoDB Settings
app.config['MONGO_DBNAME'] = 'web_queries'
app.config['MONGO_USERNAME'] = 'db_admin'
app.config['MONGO_PASSWORD'] = 'dbpass'

mongo = PyMongo(app, config_prefix='MONGO')


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
        if len(request.form['motif']) < 2:
            error = 'ERROR! Submitted motif not long enough! Please try again!'
            return render_template('/motif/create.html', error=error, motif_list=choices.AMINOACID_CHOICES)
        if mongo.db.motif.find({'sequence_motif': request.form['motif']}).limit(1).count() > 0:
            error = 'ERROR! Motif already exists in database!'
            return render_template('/motif/create.html', error=error, motif_list=choices.AMINOACID_CHOICES)
        new_motif = {
            'sequence_motif': request.form['motif'],
            'datetime_added': datetime.utcnow(),
            'user': 'default',
        }
        mongo.db.motif.insert_one(new_motif)
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
        if len(request.form.getlist('motif_list[]')) == 0:
            error = 'ERROR! No motifs selected! Please select motifs to continue analysis!'
            query = mongo.db.motif.find({
                'user': 'default',
            }).sort([
                ('datetime_added', -1),
            ])
            return render_template('/motif/select.html', error=error, query=query)
        motif_list = helpers.convert_string_ids_to_bson_objectids(request.form.getlist('motif_list[]'))
        new_query = {
            'motif_list': motif_list,
            'datetime_added': datetime.utcnow(),
            'user': 'default',
        }
        result = mongo.db.query.insert_one(new_query)
        response = app.make_response(redirect('/form/sequences/', code=302))
        response.set_cookie('query_id', str(result.inserted_id))
        return response
    else:
        if mongo.db.motif.find({'user': 'default'}).count() == 0:
            error = 'ERROR! No motifs saved in database! Please create motifs to continue analysis!'
            return render_template('/motif/select.html', error=error)
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
    return render_template('/sequences/index.html')


@app.route('/form/sequences/create/', methods=['GET', 'POST'])
def sequences_create():
    """
    Sequence creation form and database insertion.
    :return template:
    """
    if request.method == 'POST':
        if request.form['collection_type'] == 'FASTA':
            collection = helpers.format_input(collection_text=request.form['collection_textbox'],
                                              file_type=request.form['collection_type'])
            collection = helpers.format_collection(collection=collection, file_type=request.form['collection_type'])
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
    if request.method == 'POST':
        collection_list = helpers.convert_string_ids_to_bson_objectids(request.form.getlist('collection_list[]'))
        query_id = helpers.convert_string_id_to_bson_objectid(request.cookies.get('query_id'))
        mongo.db.query.update({
            '_id': query_id,
        }, {
            '$set': {
                'collection_list': collection_list,
            }
        }, upsert=False)
        return redirect('/form/options/', code=302)
    else:
        query = mongo.db.collection.find({
            'user': 'default',
        }).sort([
            ('datetime_added', -1),
        ])
        return render_template('/sequences/select.html', query=query)


@app.route('/form/options/', methods=['GET', 'POST'])
def form_options():
    if request.method == 'POST':
        query_id = helpers.convert_string_id_to_bson_objectid(request.cookies.get('query_id'))
        mongo.db.query.update({
            '_id': query_id,
        }, {
            '$set': {
                'motif_frequency': int(request.form['motif_frequency']),
                'motif_frame_size': int(request.form['motif_frame_size']),
            }
        }, upsert=False)
        return redirect('/results/', code=302)
    else:
        query_id = helpers.convert_string_id_to_bson_objectid(request.cookies.get('query_id'))
        query = mongo.db.query.find_one({'_id': query_id})
        motif_list = []
        sequence_count = 0
        # list motifs as string
        for motif_id in query['motif_list']:
            motif_query = mongo.db.motif.find_one({'_id': motif_id})
            motif_list.append(motif_query['sequence_motif'])
        motifs = ', '.join(motif_list)
        # count sequences
        for collection_id in query['collection_list']:
            collection_query = mongo.db.collection.find_one({'_id': collection_id})
            sequence_count += len(collection_query['collection'])
        return render_template('/options/index.html', motifs=motifs, sequence_count=sequence_count)

if __name__ == '__main__':
    app.run()
