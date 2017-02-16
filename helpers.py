"""
This contains
"""

import os
import re
import csv
import pathlib

from bson.objectid import ObjectId
from io import StringIO
from Bio import SeqIO

import choices


def is_allowed_file(filename):
    """
    Returns boolean value determined by if file
    is of allowed extension type
    :param filename:
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in choices.ALLOWED_EXTENSIONS


def format_textarea_text_fasta(input_text):
    """
    Convert textarea input text to list of
    BioPython-parsed sequence dictionaries
    :param input_text:
    :return:
    """
    # ensure `input_text` param is string
    if not isinstance(input_text, str):
        return False

    # ensure `input_text` param is not 0 length
    if len(input_text) == 0:
        return False

    # parse input
    fasta_list = Private.fasta_blob_to_list(input_text)
    return Private.biopython_parse_fasta_list(fasta_list)


def format_file_fasta(file_path):
    """

    :param file_path:
    :return:
    """
    # ensure file exists
    if not pathlib.Path(file_path).is_file():
        return False

    return Private.biopython_parse_fasta_file(file_path)


def convert_string_ids_to_bson_objectids(string_list):
    """
    Converts string ids taken from html to BSON
    ObjectIds readable by MongoDB
    :param string_list:
    :return list:
    """
    # ensure `string_list` is list
    if not isinstance(string_list, list):
        return False

    # ensure each element of `string_list` is string
    for string_id in string_list:
        if not isinstance(string_id, str):
            return False

    # ensure `string_list` not empty
    if len(string_list) == 0:
        return False

    objectid_list = []
    for string_id in string_list:
        objectid_list.append(ObjectId(string_id))
    return objectid_list


def write_results_to_csv(query, sequence, analysis_result):
    """

    :param query:
    :param sequence:
    :param analysis_result:
    :return:
    """

    # ensure query param is dictionary
    if not isinstance(query, dict):
        return False

    # ensure query dict includes `'_id'` key
    if '_id' not in query:
        return False

    # ensure `query['_id']` is ObjectId
    if not isinstance(query['_id'], ObjectId):
        return False

    # ensures `sequence` param is dictionary
    if not isinstance(sequence, dict):
        return False

    # ensures each `sequence` dictionary value is a string
    for key, value in sequence.items():
        if not isinstance(value, str):
            return False

    # ensure `analysis_result` is list
    if not isinstance(analysis_result, list):
        return False

    # ensure `analysis_result` contains correct data
    for result in analysis_result:
        if 'motif' not in result:
            return False
        if not isinstance(result['motif'], str):
            return False
        if 'raw_data' not in result:
            return False
        if not isinstance(result['raw_data'], list):
            return False
        if len(result['raw_data']) > 0:
            for raw_data_result in result['raw_data']:
                if 'group' not in raw_data_result:
                    return False
                if 'span' not in raw_data_result:
                    return False
        if 'motif_data' not in result:
            return False
        if not isinstance(result['motif_data'], list):
            return False
        if len(result['motif_data']) > 0:
            for motif_data_hit in result['motif_data']:
                for motif_data_result in motif_data_hit:
                    if 'group' not in motif_data_result:
                        return False
                    if 'span' not in motif_data_result:
                        return False

    # parse csv filename from `query_id` string and create file path
    csv_filename = ''.join([str(query['_id']), '.csv'])
    csv_file = os.path.join(os.getcwd(), 'downloads', csv_filename)

    # create csv file and populate header if file does not exist
    if not pathlib.Path(csv_file).is_file():
        Private.create_csv_file(csv_file)

    # write results to csv file accounting for page reloads
    with open(csv_file, 'r') as fp:
        data = fp.readlines()
        fp.close()
    if len(data) <= query['sequence_count']:
        Private.write_to_csv_file(csv_file, query, sequence, analysis_result)
    return True


class Private(object):
    @staticmethod
    def fasta_blob_to_list(fasta_blob):
        """

        :param fasta_blob:
        :return:
        """
        fasta_list = []
        for sequence_str in fasta_blob.split('>'):
            if len(sequence_str) > 0:
                fasta_list.append(''.join(['>', sequence_str]))
        return fasta_list

    @staticmethod
    def biopython_parse_fasta_list(fasta_list):
        """

        :param fasta_list:
        :return:
        """
        collection_list = []
        for sequence_str in fasta_list:
            record = SeqIO.read(StringIO(sequence_str), 'fasta')
            # print('%s' % record)
            collection_list.append({
                'sequence_id': record.id,
                'sequence_name': record.name,
                'sequence_description': record.description,
                'sequence': str(record.seq),
            })
        return collection_list

    @staticmethod
    def biopython_parse_fasta_file(file_path):
        """

        :param file_path:
        :return:
        """
        collection_list = []
        with open(file_path, 'r') as fasta_file:
            for record in SeqIO.parse(fasta_file, 'fasta'):
                collection_list.append({
                    'sequence_id': record.id,
                    'sequence_name': record.name,
                    'sequence_description': record.description,
                    'sequence': str(record.seq),
                })
        return collection_list

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
