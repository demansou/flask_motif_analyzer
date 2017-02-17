"""
This contains
"""

from .models import Sequence

import csv
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


class Private(object):
    @staticmethod
    def regex_find_iter(motif, sequence_str):
        """
        Creates a list of re.finditer() output for a list of re.finditer() hits
        :param motif:
        :param sequence_str:
        :return list:
        """
        # compile regex
        compiled_pattern = re.compile(motif)

        # gather regex matches in list
        match_list = []
        for match in re.finditer(compiled_pattern, sequence_str):
            match_details = {
                'group': match.group(),
                'span': match.span(),
            }
            match_list.append(match_details)
        return match_list

    @staticmethod
    def create_csv_file(file_path):
        """
        Takes file path and creates csv file with header row
        :param file_path:
        :return:
        """
        row = [
            'Sequence ID',
            'Sequence Description',
            'Sequence',
            'Motif Frequency',
            'Motif Frame Size',
            'Motif(s)',
            'Motif Matches',
            'Raw Data',
        ]
        with open(file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(row)

    @staticmethod
    def write_to_csv_file(file_path, query, sequence, analysis_result):
        """

        :param file_path:
        :param query:
        :param sequence:
        :param analysis_result:
        :return:
        """
        motif_matches = []
        raw_data = []
        for result in analysis_result:
            motif_matches.append(result['motif_data'])
            raw_data.append(result['raw_data'])
        row = [
            sequence['sequence_id'],
            sequence['sequence_description'],
            sequence['sequence'],
            query['motif_frequency'],
            query['motif_frame_size'],
            query['motifs_as_string'],
            motif_matches,
            raw_data,
        ]
        with open(file_path, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(row)
