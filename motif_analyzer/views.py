from __future__ import absolute_import
from motif_analyzer import app, celery
from . import helpers
from . import choices
from .tasks import analyze_sequence
from .models import Collection, Motif, Query, Result, Sequence

from bson import json_util
from bson.objectid import ObjectId
from flask import flash, request, render_template, redirect, send_file

import json
import os


@app.route('/', methods=['GET'])
def app_home():
    """
    Displays app front page
    :return template:
    """
    response = app.make_response(render_template('frontpage.html'))
    response.set_cookie('query_id', '')
    response.set_cookie('collection_id_list', '')
    response.set_cookie('motif_id_list', '')
    response.set_cookie('user', 'default')
    return response


@app.route('/sequences/', methods=['GET', 'POST'])
def select_sequences():
    """
    Displays sequence collection selection form
    :return:
    """
    if request.method == 'GET':
        collections = Collection.find(user=request.cookies['user'])
        return render_template('/sequences/select.html', collections=collections)

    ###############
    # POST METHOD #
    ###############

    # ensure at least one collection selected
    if len(request.form.getlist('collection_list[]')) == 0:
        flash('ERROR! Must select at least one collection to continue')
        return redirect(request.url)

    # move to motif selection
    response = app.make_response(redirect('/motifs/'))
    response.set_cookie('collection_id_list', ','.join(request.form.getlist('collection_list[]')))
    return response


@app.route('/sequences/paste/', methods=['GET', 'POST'])
def paste_sequences():
    """
    Displays sequence file paste form
    :return:
    """
    if request.method == 'GET':
        return render_template('/sequences/paste.html', allowed_extensions=choices.INPUT_TYPES)

    ###############
    # POST METHOD #
    ###############

    # insert collection information into database
    collection_id = Collection.insert_one(
        collection_name=request.form['collection_name'],
        collection_type=request.form['collection_type'],
        user=request.cookies['user']
    )

    # ensure collection id is inserted into MongoDB before inserting sequences into MongoDB
    if not collection_id:
        flash('ERROR! Error inserting collection data into database! Please try again!')
        return redirect(request.url)

    # parse sequences with BioPython and insert parsed sequences into MongoDB
    result = helpers.insert_fasta_paste(request.form['collection_textbox'], collection_id, request.cookies['user'])

    # ensure sequences are inserted into database
    if result == 0:
        Collection.delete_one(document_id=collection_id)
        flash('ERROR! Error inserting collection data into database! Please try again!')
        return redirect(request.url)

    return redirect('/sequences/')


@app.route('/sequences/upload/', methods=['GET', 'POST'])
def upload_sequences():
    """
    displays sequence file upload form
    :return:
    """
    if request.method == 'GET':
        return render_template('/sequences/upload.html', allowed_extensions=choices.INPUT_TYPES)

    ###############
    # POST METHOD #
    ###############

    # ensure file present in request
    if 'fasta_file' not in request.files:
        flash('ERROR! File not found in upload form! Please try again!')
        return redirect(request.url)

    # insert collection information into database
    collection_id = Collection.insert_one(
        collection_name=request.form['collection_name'],
        collection_type=request.form['collection_type'],
        user=request.cookies['user']
    )

    # ensure collection id is inserted into MongoDB before inserting sequences into MongoDB
    if not collection_id:
        flash('ERROR! Error inserting collection data into database! Please try again!')
        return redirect(request.url)

    # use request file to parse sequences with BioPython and insert parsed sequences into MongoDB
    file = request.files['fasta_file']
    if file and helpers.is_allowed_file(file.filename):
        result = helpers.insert_fasta_file(file.read(), collection_id, request.cookies['user'])

        # ensure sequences inserted into database
        if result == 0:
            Collection.delete_one(document_id=collection_id)
            flash('ERROR! Error inserting collection sequence data into database! Please try again!')
            return redirect(request.url)

        return redirect('/sequences/')

    # catchall for file errors
    flash('ERROR! Error in file or non-permitted file name! Please try again!')
    return redirect(request.url)


@app.route('/motifs/', methods=['GET', 'POST'])
def select_motifs():
    """
    Displays motif selection form
    :return:
    """
    if request.method == 'GET':
        motifs = Motif.find(user=request.cookies['user'])
        return render_template('/motif/select.html', motifs=motifs)

    ###############
    # POST METHOD #
    ###############

    # ensure at least one motif selected
    if len(request.form.getlist('motif_list[]')) == 0:
        flash('ERROR! Must select at least one motif to continue')
        return redirect(request.url)

    # move to options selection
    response = app.make_response(redirect('/options/'))
    response.set_cookie('motif_id_list', ','.join(request.form.getlist('motif_list[]')))
    return response


@app.route('/motifs/create/', methods=['GET', 'POST'])
def create_motifs():
    """
    Display motif creation form
    :return:
    """
    if request.method == 'GET':
        return render_template('/motif/create.html', amino_acids=choices.AMINOACID_CHOICES)

    ################
    # POST REQUEST #
    ################

    # ensure motif is at least semi-selective
    if len(request.form['motif']) < 3:
        flash('ERROR! Motif must contain at least 3 amino acids!')
        return redirect(request.url)

    # redirect to motif selection form if motif already present in database
    if Motif.find(motif=request.form['motif']).count() >= 1:
        flash('ERROR! Motif already present in database!')
        return redirect('/motifs/')

    # insert motif into database
    result = Motif.insert_one(motif=request.form['motif'], user=request.cookies['user'])

    # ensure motif is added to database
    if not result:
        flash('ERROR! Error inserting new motif into database! Please try again!')
        return redirect(request.url)

    # after successful insertion, return to motif selection form
    return redirect('/motifs/')


@app.route('/options/', methods=['GET', 'POST'])
def select_options():
    """
    Displays options selection form
    :return:
    """
    if request.method == 'GET':
        # query MongoDB with each ObjectId for motifs
        motif_str_list = []
        for motif_id in request.cookies['motif_id_list'].split(','):
            motif_str_list.append(Motif.find_one(document_id=ObjectId(motif_id))['motif'])
        motif_str_list = ', '.join(motif_str_list)

        # query MongoDB with each ObjectId for count
        sequence_count = 0
        for collection_id in request.cookies['collection_id_list'].split(','):
            sequence_count += Sequence.find(collection_id=ObjectId(collection_id)).count()

        return render_template('/options/index.html', motif_str_list=motif_str_list,
                               sequence_count=sequence_count)

    ###############
    # POST METHOD #
    ###############

    motif_id_list = request.cookies['motif_id_list'].split(',')
    collection_id_list = request.cookies['collection_id_list'].split(',')
    query_id = Query.insert_one(
        motif_id_list=motif_id_list,
        collection_id_list=collection_id_list,
        motif_frequency=int(request.form['motif_frequency']),
        motif_frame_size=int(request.form['motif_frame_size']),
        user=request.cookies['user']
    )

    if not query_id:
        flash('ERROR! Error inserting new query into database! Please try again!')
        return redirect(request.url)

    response = app.make_response(redirect('/results/'))
    response.set_cookie('query_id', str(query_id))
    return response


@app.route('/results/', methods=['GET'])
def view_results():
    """
    Displays analysis results
    :return:
    """
    # ensures a query id is present in cookies
    if not request.cookies['query_id'] or len(request.cookies['query_id']) == 0:
        flash('ERROR! Query cookie not present! Please start over!')
        return redirect('/')

    query = Query.find_one(document_id=ObjectId(request.cookies['query_id']))

    # ensures that query id is valid
    if not query:
        flash('ERROR! Query not found in database! Please start over!')
        return redirect('/')

    # query MongoDB with each ObjectId for motifs
    motif_str_list = []
    for motif_id in query['motif_id_list']:
        motif_str_list.append(Motif.find_one(document_id=ObjectId(motif_id))['motif'])
    motif_str_list = ', '.join(motif_str_list)

    # query MongoDB with each ObjectId for count
    sequence_count = 0
    for collection_id in query['collection_id_list']:
        sequence_count += Sequence.find(collection_id=ObjectId(collection_id)).count()

    return render_template('/results/index.html', motif_str_list=motif_str_list, sequence_count=sequence_count,
                           motif_frequency=query['motif_frequency'], motif_frame_size=query['motif_frame_size'])


@app.route('/start_analysis/', methods=['POST'])
def start_analysis():
    """
    Starts analysis results
    :return:
    """
    # ensure query id is stored in cookies
    if not request.cookies['query_id'] or len(request.cookies['query_id']) == 0:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Query id cookie invalid!',
            'started': False,
        })

    query = Query.find_one(document_id=ObjectId(request.cookies['query_id']))

    # ensure query is returned from MongoDB
    if not query:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Query not found in database!',
            'started': False,
        })

    # clear previous query results for instances such as page reload
    Result.delete_many(query_id=query['_id'])

    # make list of motifs from query
    motif_list = []
    for motif_id in query['motif_id_list']:
        motif_list.append(Motif.find_one(document_id=ObjectId(motif_id))['motif'])

    # ensure motifs in motif list
    if len(motif_list) == 0:
        return json.dumps({
            'error': True,
            'message': 'ERROR! No motifs to run analysis with!',
            'started': False,
        })

    # do analysis for each sequence
    for collection_id in query['collection_id_list']:
        sequences = Sequence.find(collection_id=ObjectId(collection_id))

        # ensure sequences are returned
        if not sequences:
            return json.dumps({
                'error': True,
                'message': 'ERROR! No sequences to run analysis with!',
                'started': False,
            })

        for sequence in sequences:
            analyze_sequence.delay(
                query_id=str(query['_id']),
                sequence_description=sequence['sequence_description'],
                sequence=sequence['sequence'],
                motif_list=motif_list,
                motif_frequency=query['motif_frequency'],
                motif_frame_size=query['motif_frame_size'],
                user=request.cookies['user']
            )

    return json.dumps({
        'error': False,
        'message': 'Analysis started!',
        'started': True,
    })


@app.route('/count_results/', methods=['POST'])
def count_results():
    """
    Counts completed analysis results
    :return:
    """
    # ensure query id is stored in cookies
    if not request.cookies['query_id'] or len(request.cookies['query_id']) == 0:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Query id cookie invalid!',
            'complete': False,
        })

    query = Query.find_one(document_id=ObjectId(request.cookies['query_id']))

    # ensure query is returned from MongoDB
    if not query:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Query not found in database!',
            'complete': False,
        })

    # query MongoDB with each ObjectId for count
    sequence_count = 0
    for collection_id in query['collection_id_list']:
        sequence_count += Sequence.find(collection_id=ObjectId(collection_id)).count()

    # query MongoDB for result count from query
    result_count = Result.find(query_id=query['_id']).count()

    if result_count < sequence_count:
        return json.dumps({
            'error': False,
            'message': '{0}/{1}' % ([result_count, sequence_count]),
            'complete': False,
        })

    return json.dumps({
        'error': False,
        'message': '{0}/{1}' % ([result_count, sequence_count]),
        'complete': True
    })


@app.route('/get_results/', methods=['POST'])
def get_results():
    """
    Retrieves results from MongoDB and sends to client
    :return:
    """
    # ensure query id is stored in cookies
    if not request.cookies['query_id'] or len(request.cookies['query_id']) == 0:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Query id cookie invalid!',
            'data': []
        })

    results = Result.find(query_id=ObjectId(request.cookies['query_id']))

    # ensure results are returned from MongoDB
    if not results:
        return json.dumps({
            'error': True,
            'message': 'ERROR! No results found in database!',
            'data': []
        })

    # generate csv file name and write header
    file_path = helpers.create_csv_file(request.cookies['query_id'])

    if not file_path:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Unable to create CSV file!',
            'data': []
        })

    # get query data for csv file
    query = Query.find_one(document_id=ObjectId(request.cookies['query_id']))

    if not query:
        return json.dumps({
            'error': True,
            'message': 'ERROR! Unable to retrieve query for CSV data!',
            'data': []
        })

    # create list of motifs
    motif_list = []
    for motif_id in query['motif_id_list']:
        motif_list.append(Motif.find_one(document_id=ObjectId(motif_id))['motif'])

    # create list of results and csv file
    result_list = []
    for result in results:
        write_result = helpers.write_to_csv_file(
            file_path=file_path,
            sequence_description=result['sequence_description'],
            sequence=result['sequence'],
            motif_list=motif_list,
            motif_frequency=query['motif_frequency'],
            motif_frame_size=query['motif_frame_size'],
            analysis=result['analysis']
        )
        if not write_result:
            return json.dumps({
                'error': True,
                'message': 'ERROR! Error writing result to database!',
                'data': []
            })
        result_list.append(result)

    return json.dumps({
        'error': False,
        'message': '',
        'data': result_list,
    }, default=json_util.default)


@app.route('/download_results/', methods=['GET'])
def get_file():
    file_name = ''.join([request.cookies.get('query_id'), '.csv'])
    file_path = os.path.join(os.getcwd(), 'motif_analyzer', 'downloads', file_name)
    return send_file(file_path, attachment_filename=file_name, as_attachment=True, mimetype='text/csv')
