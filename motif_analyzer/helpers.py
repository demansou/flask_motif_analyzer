"""
This contains
"""

from . import choices
from .models import Sequence

from Bio import SeqIO
import csv
from io import StringIO, BytesIO
import os
import pathlib
import random
import string


def is_allowed_file(filename):
    """
    Returns boolean value determined by if file
    is of allowed extension type
    :param filename:
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in choices.ALLOWED_EXTENSIONS


def insert_fasta_paste(textarea_str, collection_id, user):
    """

    :param textarea_str:
    :param collection_id:
    :param user:
    :return:
    """
    sequences_inserted = 0
    for record in SeqIO.parse(StringIO(textarea_str), 'fasta'):
        sequence_id = Sequence.insert_one(
            collection_id=collection_id,
            sequence_id=record.id,
            sequence_name=record.name,
            sequence_description=record.description,
            sequence=str(record.seq),
            user=user
        )
        if sequence_id:
            sequences_inserted += 1
    return sequences_inserted


def insert_fasta_file(file_stream, collection_id, user):
    """
    Converts file stream to StringIO and parses sequence
    records using BioPython and inserts into MongoDB
    :param file_stream:
    :param collection_id:
    :param user:
    :return:
    """
    sequences_inserted = 0
    for record in SeqIO.parse(StringIO(BytesIO(file_stream).read().decode('utf-8')), 'fasta'):
        sequence_id = Sequence.insert_one(
            collection_id=collection_id,
            sequence_id=record.id,
            sequence_name=record.name,
            sequence_description=record.description,
            sequence=str(record.seq),
            user=user
        )
        if sequence_id:
            sequences_inserted += 1
    return sequences_inserted


def create_csv_file(query_id):
    """
    Takes file path and creates csv file with header row
    :param query_id:
    :return:
    """
    here = os.path.dirname(__file__)
    file_name = ''.join([query_id, '.csv'])
    file_path = os.path.join(here, 'downloads', file_name)

    if pathlib.Path(file_path).is_file():
        os.remove(file_path)

    row = [
        'Sequence Description',
        'Sequence',
        'Motif(s)',
        'Motif Frequency',
        'Motif Frame Size',
        'Analysis Results',
    ]

    try:
        with open(file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(row)
            return file_path
    except (FileNotFoundError, PermissionError) as e:
        print('{0}'.format(e))
        print('here: {0}'.format(here))
        print('file path: {0}'.format(file_path))
        return None


def write_to_csv_file(file_path, sequence_description, sequence, motif_list, motif_frequency, motif_frame_size,
                      analysis):
    """
    Writes results to csv file line
    :param file_path:
    :param sequence_description:
    :param sequence:
    :param motif_list:
    :param motif_frequency:
    :param motif_frame_size:
    :param analysis:
    :return:
    """

    here = os.path.dirname(__file__)

    row = [
        sequence_description,
        sequence,
        motif_list,
        motif_frequency,
        motif_frame_size,
        analysis,
    ]

    try:
        with open(file_path, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(row)
        return True
    except (FileNotFoundError, PermissionError) as e:
        print('{0}'.format(e))
        print('here: {0}'.format(here))
        print('{0}'.format(file_path))
        return None


def format_html(sequence_description, sequence, analysis):
    outer_table_header = '<tr><th>Sequence</th><th>{0}</th></tr>'.format(sequence_description)
    outer_table_results = '<tr><td><strong>Motif Matches</strong></td><td>{0}</td></tr>'.format(
        format_analysis_html(sequence_description, sequence, analysis)
    )
    result_html = '<table class=\"table table-bordered table-responsive\">{0}{1}</table>'.format(
        outer_table_header,
        outer_table_results
    )
    return result_html


def format_analysis_html(sequence_description, sequence, analysis):
    inner_table_html = ''
    for data in analysis:
        inner_table = ''
        for i, key in enumerate(data):
            table_header = '<tr><th>Motif</th><th>{0}</th><th></th></tr>'.format(key)
            inner_table = '{0}{1}'.format(
                table_header,
                parse_analysis_result_data(data[key], sequence, sequence_description)
            )
        inner_table = '<table class=\"table table-bordered table-responsive\">{0}</table>'.format(inner_table)
        inner_table_html = '{0}{1}'.format(inner_table_html, inner_table)

    return inner_table_html


def parse_analysis_result_data(analysis_data, sequence, sequence_description):
    parsed_data = ''
    for motif_data in analysis_data:
        result_row = ''
        for i, motif_match in enumerate(motif_data):
            if i < len(motif_data) - 1:
                formatted_match = 'Amino Acid Match: \"{0}\", Location: [{1},{2}]<br>'.format(
                    motif_match['match'],
                    motif_match['span'][0],
                    motif_match['span'][1]
                )
            else:
                formatted_match = 'Amino Acid Match: \"{0}\", Location: [{1},{2}]'.format(
                    motif_match['match'],
                    motif_match['span'][0],
                    motif_match['span'][1]
                )

            if i < len(motif_data) - 1:
                result_row = '{0}{1}'.format(result_row, formatted_match)
            else:
                result_row = '<tr><td></td><td>{0}{1}</td><td>{2}</td></tr>'.format(
                    result_row,
                    formatted_match,
                    parse_modal_button(motif_data, sequence, sequence_description)
                )
        parsed_data = '{0}{1}'.format(parsed_data, result_row)
    return parsed_data


def parse_modal_button(motif_match, sequence, sequence_description):
    """

    :param motif_match:
    :param sequence:
    :param sequence_description:
    :return:
    """
    generated_id = generate_id(16)
    button_html = '<button class=\"btn btn-primary btn-block\" data-toggle=\"modal\" data-target=\"#{0}\">Get Motif' \
                  '</button>'.format(generated_id)
    modal_header_close = '<button type=\"button\" class=\"close\" data-dismiss=\"modal\"><span aria-hidden=\"true\">' \
                         '&times;</span><span class=\"sr-only\">Close</span></button>'
    modal_header_title = '<h4 class=\"modal-title\">{0}</h4>'.format(sequence_description)
    modal_header = '{0}{1}'.format(modal_header_close, modal_header_title)
    modal_content = '<div class=\"modal-header\">{0}</div><div class=\"modal-body\"><p class=\"is-breakable\">{1}' \
                    '</p></div>'.format(modal_header, highlight_sequence_motif_frame(motif_match, sequence))
    modal_inner = '<div class=\"modal-dialog\"><div class=\"modal-content\">{0}</div></div>'.format(modal_content)
    modal_html = '<div class=\"modal modal-fullscreen fade\" id=\"{0}\" role=\"dialog\" aria-hidden=\"true\">{1}' \
                 '</div>'.format(generated_id, modal_inner)
    modal_button_html = '{0}{1}'.format(button_html, modal_html)
    return modal_button_html


def highlight_sequence_motif_frame(motif_data, sequence):
    # print('%s' % motif_data)
    motif_frame_start = motif_data[0]['span'][0]
    motif_frame_end = motif_data[len(motif_data) - 1]['span'][1]
    # print('start: {0}\tend: {1}'.format(motif_frame_start, motif_frame_end))
    parsed_sequence = '{0}<strong><span class=\"motif-string\" id=\"{1}\">{2}</span></strong>{3}'.format(
        sequence[:motif_frame_start],
        motif_data[0]['group'],
        sequence[motif_frame_start:motif_frame_end],
        sequence[motif_frame_end:]
    )
    return parsed_sequence


def generate_id(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(int(length)))
