from motif_analyzer import app, mongo
from . import helpers
from . import choices
from .models import Collection, Motif, Query, Result, Sequence

from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
from flask import flash, request, render_template, redirect, send_file
from werkzeug.utils import secure_filename

import os
import json


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
        collections = Collection.find(user=request.cookies['user'])
        return render_template('/sequences/select.html', collections=collections)

    # move to motif selection
    response = app.make_response(redirect('/motifs/'))
    response.set_cookie('collection_id_list', ','.join(request.form.getlist('collection_list[]')))
    return response


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
        motifs = Motif.find(user=request.cookies['user'])
        return render_template('/motif/select.html', motifs=motifs)

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
        return render_template('/motif/create.html', amino_acids=choices.AMINOACID_CHOICES)

    # redirect to motif selection form if motif already present in database
    if Motif.find(motif=request.form['motif']).count() >= 1:
        flash('ERROR! Motif already present in database!')
        return redirect('/motifs/')

    # insert motif into database
    result = Motif.insert_one(motif=request.form['motif'], user=request.cookies['user'])

    # ensure motif is added to database
    if not result:
        flash('ERROR! Error inserting new motif into database! Please try again!')
        return render_template('/motif/create.html', amino_acids=choices.AMINOACID_CHOICES)

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

    result = Query.find_one(document_id=ObjectId(request.cookies['query_id']))

    # ensures that query id is valid
    if not result:
        flash('ERROR! Query not found in database! Please start over!')
        return redirect('/')

    # query MongoDB with each ObjectId for motifs
    motif_str_list = []
    for motif_id in result['motif_id_list']:
        motif_str_list.append(Motif.find_one(document_id=ObjectId(motif_id))['motif'])
    motif_str_list = ', '.join(motif_str_list)

    # query MongoDB with each ObjectId for count
    sequence_count = 0
    for collection_id in request.cookies['collection_id_list'].split(','):
        sequence_count += Sequence.find(collection_id=ObjectId(collection_id)).count()

    return render_template('/results/index.html', motif_str_list=motif_str_list, sequence_count=sequence_count,
                           motif_frequency=result['motif_frequency'], motif_frame_size=result['motif_frame_size'])
