import os
import random
import string

from bson.objectid import ObjectId
from Bio import SeqIO


def format_input(collection_text, file_type):
    """
    Breaks html textarea input into BioPython SeqIO format
    :param collection_text:
    :param file_type:
    :return:
    """
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


def convert_string_id_to_bson_objectid(string_id):
    """
    Converts single string id taken from html
    to BSON ObjectId readable by MongoDB
    :param string_id:
    :return bson.ObjectId object:
    """
    return ObjectId(string_id)


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
