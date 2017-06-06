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
    return response


@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'GET':
        response = app.make_response(render_template('upload.html'))
        return response

    response = app.make_response(render_template('confirmation.html'))
    response.set_cookie('query_id', '')
    return response
