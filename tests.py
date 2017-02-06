import helpers


def test_analyze_sequence_output():
    """
    Tests output of helpers.analyze_sequence() with a simple set of parameters
    :return:
    """
    sequence = {
        'sequence': """
    MEQDWQPGEEVTPGPEPCSKGQAPLYPIVHVTELKHTDPNFPSNSNAVGTSSGWNRIGTG
    CSHTWDWRFSCTQQALLPLLGAWEWSIDTEAGGGRREQSQKPCSNGGPAAAGEGRVLPSP
    CFPWSTCQAAIHKVCRWQGCTRPALLAPSLATLKEHSYP
    """,
    }
    motif_list = ['[ST]Q']
    motif_frequency = 3
    motif_frame_size = 100
    return helpers.analyze_sequence(sequence=sequence, motif_list=motif_list, motif_frequency=motif_frequency,
                                    motif_frame_size=motif_frame_size)

print('%s' % test_analyze_sequence_output())
