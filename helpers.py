import os
import random
import string
import re

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

        # with matches, analyze in regards to `motif_frequency` and `motif_frame_size`
        motif_match_list = []
        num_motifs = 0
        for match in raw_match_list:
            # `loose` match (`tight` match would be match['span'][0])
            substr_start = match['span'][1]
            substr_end = substr_start + motif_frame_size
            if substr_end > len(sequence['sequence']):
                substr_end = len(sequence['sequence'])
            motif_list = Private.regex_find_iter(motif, sequence['sequence'][substr_start:substr_end])
            if len(motif_list) >= motif_frequency:
                motif_boolean = True
                num_motifs += 1
                motif_match_details = {
                    'start': match,
                    'motif': motif_list,
                }
                motif_match_list.append(motif_match_details)

        # for match in match_list compile sequence result dictionary
        sequence_result = {
            'motif': motif,
            'raw_data': raw_match_list,
            'total_matches': len(raw_match_list),
            'motif_data': motif_match_list,
            'motif_matches': num_motifs,
        }
        result_list.append(sequence_result)

    return result_list, motif_boolean


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
