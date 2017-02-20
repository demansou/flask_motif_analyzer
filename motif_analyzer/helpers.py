"""
This contains
"""

from .models import Sequence

import csv
import os
import pathlib
import re
from io import StringIO, BytesIO

from Bio import SeqIO

from motif_analyzer import choices


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
    file_name = ''.join([query_id, '.csv'])
    file_path = os.path.join(os.getcwd(), 'motif_analyzer', 'downloads', file_name)
    print('{0}'.format(file_path))

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
        print('%s' % e)
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
    except FileNotFoundError:
        return None

