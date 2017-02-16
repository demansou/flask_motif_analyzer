from motif_analyzer import mongo, celery
from . import helpers

from datetime import datetime


@celery.task()
def analyze_sequence(query, sequence, motif_list, motif_frequency, motif_frame_size):
    """
    Performs sequence analysis on a single BioPython Sequence object using
    motif parameters
    :param query:
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
        raw_match_list = helpers.Private.regex_find_iter(motif, sequence['sequence'])

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

    # append result to csv and database
    write_result = helpers.write_results_to_csv(query, sequence, result_list)
    if write_result is not False:
        mongo.db.result.insert_one({
            'query_id': query['_id'],
            'sequence': sequence,
            'analysis': result_list,
            'has_motif': motif_boolean,
            'datetime_added': datetime.utcnow(),
        })