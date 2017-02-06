import os
import random
import string
import re
import csv
import pathlib

from bson.objectid import ObjectId

from Bio import SeqIO


def format_input(collection_text, file_type):
    """
    Breaks html textarea input into BioPython Seq object format
    :param collection_text:
    :param file_type:
    :return:
    """
    if len(collection_text) == 0:
        return False
    if file_type == 'FASTA':
        return Private.read_fasta_string(collection_text)
    else:
        return False


def format_collection(collection, file_type):
    """
    Breaks BioPython Seq objects into strings for database entry
    :param collection:
    :param file_type:
    :return list:
    """
    if collection is False:
        return False
    if file_type == 'FASTA':
        collection_list = []
        for sequence in collection:
            sequence_dict = {
                'sequence': str(sequence.seq),
                'sequence_id': sequence.id,
                'sequence_name': sequence.name,
                'sequence_description': sequence.description,
            }
            collection_list.append(sequence_dict)
        return collection_list
    else:
        return False


def convert_string_ids_to_bson_objectids(string_list):
    """
    Converts string ids taken from html to BSON
    ObjectIds readable by MongoDB
    :param string_list:
    :return list:
    """
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
    # parse csv filename from `query_id` string and create file path
    csv_filename = ''.join([str(query['_id']), '.csv'])
    csv_file = os.path.join(os.getcwd(), 'downloads', csv_filename)

    # create csv file and populate header if file does not exist
    if not pathlib.Path(csv_file).is_file():
        Private.create_csv_file(csv_file)

    # write results to csv file
    Private.write_to_csv_file(csv_file, query, sequence, analysis_result)


class Private(object):
    @staticmethod
    def read_fasta_string(fasta_string):
        """
        Reads fasta string to file and returns sequences as list object
        BioPython SeqIO requires fasta string in a file
        :param fasta_string:
        :return object:
        """
        fasta_file_name = ''.join([Private.generate_id(16), '.txt'])
        fasta_file = os.path.join(os.getcwd(), 'tmp', fasta_file_name)
        fp = open(fasta_file, 'w')
        fp.write(fasta_string)
        fp.close()
        sequence_object = SeqIO.parse(open(fasta_file), 'fasta')
        try:
            os.remove(fasta_file)
        except OSError:
            pass
        return sequence_object

    @staticmethod
    def generate_id(length):
        """
        generates a randomized string of alphanumerics of length specified
        :param length:
        :return string:
        """
        # from http://stackoverflow.com/a/23728630/2213647
        valid_random_alphanum = string.ascii_letters + string.digits
        return ''.join(random.SystemRandom().choice(valid_random_alphanum) for _ in range(length))

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
