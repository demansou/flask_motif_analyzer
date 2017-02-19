from __future__ import absolute_import
from . import celery
from .models import Result, Sequence

from bson import ObjectId
import re


@celery.task()
def queue_analysis(collection_id_list, query_id, motif_list, motif_frequency, motif_frame_size, user):
    """

    :param collection_id_list:
    :param query_id:
    :param motif_list:
    :param motif_frequency:
    :param motif_frame_size:
    :param user:
    :return:
    """
    for collection_id in collection_id_list:
        sequences = Sequence.find(collection_id=ObjectId(collection_id))

        for sequence in sequences:
            analyze_sequence.delay(
                query_id=query_id,
                sequence_description=sequence['sequence_description'],
                sequence=sequence['sequence'],
                motif_list=motif_list,
                motif_frequency=motif_frequency,
                motif_frame_size=motif_frame_size,
                user=user
            )


@celery.task()
def analyze_sequence(query_id, sequence_description, sequence, motif_list, motif_frequency, motif_frame_size, user):
    """
    Analyzes single sequence and inserts
    results of analysis into MongoDB
    :param query_id:
    :param sequence_description:
    :param sequence:
    :param motif_list:
    :param motif_frequency:
    :param motif_frame_size:
    :param user:
    :return:
    """
    sequence_regex_matches = []
    has_motif = False

    for motif_str in motif_list:
        motif_regex = re.compile(motif_str)
        regex_match_list = []

        for match in motif_regex.finditer(sequence):
            substr_start = int(match.start())
            substr_end = substr_start + motif_frame_size
            substr_analysis = [match for match in motif_regex.finditer(sequence[substr_start:substr_end])]
            substr_match_list = []

            if len(substr_analysis) >= motif_frequency:
                for substr_match in substr_analysis:
                    substr = {
                        'match': substr_match.group(),
                        'span': [(substr_start + substr_match.span()[0]), (substr_start + substr_match.span()[1])]
                    }
                    substr_match_list.append(substr)
                has_motif = True
                regex_match_list.append(substr_match_list)
        regex_data = {
            motif_str: regex_match_list
        }
        sequence_regex_matches.append(regex_data)

    Result.insert_one(
        query_id=ObjectId(query_id),
        sequence_description=sequence_description,
        sequence=sequence,
        analysis=sequence_regex_matches,
        has_motif=has_motif,
        user=user
    )
