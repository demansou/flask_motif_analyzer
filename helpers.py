import os
import re
import csv
import pathlib

from bson.objectid import ObjectId

from io import StringIO

from Bio import SeqIO


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


def analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size):
    """
    Performs sequence analysis on a single BioPython Sequence object using
    motif parameters
    :param sequence:
    :param motif_list:
    :param motif_frequency:
    :param motif_frame_size:
    :return:
    """
    # ensures `sequence` param is dictionary
    if not isinstance(sequence, dict):
        return False

    # ensures each `sequence` dictionary value is a string
    for key, value in sequence.items():
        if not isinstance(value, str):
            return False

    # ensures that `motif_list` param is list
    if not isinstance(motif_list, list):
        return False

    # ensures that `motif_list` param list is not empty
    if len(motif_list) == 0:
        return False

    # ensures that each item in `motif_list` param list is a string
    for motif in motif_list:
        if not isinstance(motif, str):
            return False

    # ensures that `motif_frequency` param is an integer
    if not isinstance(motif_frequency, int):
        return False

    # ensures that `motif_frequency` param falls within a range
    if motif_frequency < 2 or motif_frequency > 10:
        return False

    # ensures that `motif_frame_size` param is an integer
    if not isinstance( motif_frame_size, int):
        return False

    # ensures that `motif_frame_size` param falls within a range
    if motif_frame_size < 10 or motif_frame_size > 1000:
        return False

    result_list = []
    motif_boolean = False
    for motif in motif_list:
        # get all motif matches as list
        raw_match_list = Private.regex_find_iter(motif, sequence['sequence'])

        # filter out sequences which don't have enough motifs in overall sequence
        motif_filter_list = []
        if len(raw_match_list) >= motif_frequency:
            # print('%s' % raw_match_list)

            for index, match in enumerate(raw_match_list):
                temp_list = []

                # get motif frame
                substr_start = match['span'][0]
                substr_end = substr_start + motif_frame_size

                # start temp list
                temp_list.append(match)

                # start iterating at next index of `raw_match_list`
                i = index + 1
                while i < len(raw_match_list):
                    if raw_match_list[i]['span'][0] <= substr_end:
                        temp_list.append(raw_match_list[i])
                    i += 1

                # if `temp_list` is gte than `motif_frequency`, push
                if len(temp_list) >= motif_frequency:
                    # print('MATCH: %s' % temp_list)
                    motif_filter_list.append(temp_list)
                    motif_boolean = True

        # for match in match_list compile sequence result dictionary
        sequence_result = {
            'motif': motif,
            'raw_data': raw_match_list,
            'motif_data': motif_filter_list,
        }
        result_list.append(sequence_result)

    return result_list, motif_boolean


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
        # print('%d' % len(data))
        Private.write_to_csv_file(csv_file, query, sequence, analysis_result)
    return True


class Private(object):
    @staticmethod
    def fasta_blob_to_list(fasta_blob):
        fasta_list = []
        for sequence_str in fasta_blob.split('>'):
            if len(sequence_str) > 0:
                fasta_list.append(''.join(['>', sequence_str]))
        return fasta_list

    @staticmethod
    def biopython_parse_fasta_list(fasta_list):
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
