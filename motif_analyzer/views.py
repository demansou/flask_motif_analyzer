from motif_analyzer import app

from flask import flash, request, render_template, redirect, send_file


@app.route('/', methods=['GET'])
def app_home():
    """
    Displays app front page
    :return template:
    """
    response = app.make_response(render_template('frontpage.html'))
    response.set_cookie('query_id', '')
    response.set_cookie('motif_id_list', '')
    return response


@app.route('/upload', methods=['POST'])
def file_upload():
    return redirect('/')
