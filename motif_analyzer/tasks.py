from . import celery
from .models import Result

from bson import ObjectId
import re


@celery.task(name='app.motif_analysis')
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
