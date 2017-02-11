import unittest
import os
import pathlib

import helpers

from bson import ObjectId


class TestFormatTextareaText(unittest.TestCase):

    def test_invalid_input_text_type(self):
        input_text = 123
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

        input_text = True
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

        input_text = []
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

        input_text = {}
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

        input_text = ()
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

    def test_zero_length_input_text(self):
        input_text = ''
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

    def test_string_input_text_short_string(self):
        input_text = 'ASDF'
        self.assertNotEqual(helpers.format_textarea_text_fasta(input_text), False)
        self.assertEquals(len(helpers.format_textarea_text_fasta(input_text)), 1)
        self.assertEquals(helpers.format_textarea_text_fasta(input_text), [{
            'sequence_id': input_text,
            'sequence_name': input_text,
            'sequence_description': input_text,
            'sequence': '',
        }])

    def test_string_input_text_valid_string(self):
        input_text = """>sp|P86434|AAS1_HUMAN Putative uncharacterized protein ADORA2A-AS1 OS=Homo sapiens GN=ADORA2A-AS1 PE=5 SV=1
        MEQDWQPGEEVTPGPEPCSKGQAPLYPIVHVTELKHTDPNFPSNSNAVGTSSGWNRIGTG
        CSHTWDWRFSCTQQALLPLLGAWEWSIDTEAGGGRREQSQKPCSNGGPAAAGEGRVLPSP
        CFPWSTCQAAIHKVCRWQGCTRPALLAPSLATLKEHSYP
        """
        self.assertNotEqual(helpers.format_textarea_text_fasta(input_text), False)
        self.assertEquals(len(helpers.format_textarea_text_fasta(input_text)), 1)
        self.assertEquals(helpers.format_textarea_text_fasta(input_text), [{
            'sequence_id': 'sp|P86434|AAS1_HUMAN',
            'sequence_name': 'sp|P86434|AAS1_HUMAN',
            'sequence_description': 'sp|P86434|AAS1_HUMAN Putative uncharacterized protein ADORA2A-AS1 OS=Homo sapiens GN=ADORA2A-AS1 PE=5 SV=1',
            'sequence': 'MEQDWQPGEEVTPGPEPCSKGQAPLYPIVHVTELKHTDPNFPSNSNAVGTSSGWNRIGTGCSHTWDWRFSCTQQALLPLLGAWEWSIDTEAGGGRREQSQKPCSNGGPAAAGEGRVLPSPCFPWSTCQAAIHKVCRWQGCTRPALLAPSLATLKEHSYP'
        }])

    def test_string_input_text_valid_string_multi(self):
        input_text = """>sp|P86434|AAS1_HUMAN Putative uncharacterized protein ADORA2A-AS1 OS=Homo sapiens GN=ADORA2A-AS1 PE=5 SV=1
        MEQDWQPGEEVTPGPEPCSKGQAPLYPIVHVTELKHTDPNFPSNSNAVGTSSGWNRIGTG
        CSHTWDWRFSCTQQALLPLLGAWEWSIDTEAGGGRREQSQKPCSNGGPAAAGEGRVLPSP
        CFPWSTCQAAIHKVCRWQGCTRPALLAPSLATLKEHSYP
        >sp|Q9UDR5|AASS_HUMAN Alpha-aminoadipic semialdehyde synthase, mitochondrial OS=Homo sapiens GN=AASS PE=1 SV=1
        MLQVHRTGLGRLGVSLSKGLHHKAVLAVRREDVNAWERRAPLAPKHIKGITNLGYKVLIQ
        PSNRRAIHDKDYVKAGGILQEDISEACLILGVKRPPEEKLMSRKTYAFFSHTIKAQEANM
        """
        self.assertNotEqual(helpers.format_textarea_text_fasta(input_text), False)
        self.assertEquals(len(helpers.format_textarea_text_fasta(input_text)), 2)
        self.assertEquals(helpers.format_textarea_text_fasta(input_text), [{
            'sequence_id': 'sp|P86434|AAS1_HUMAN',
            'sequence_name': 'sp|P86434|AAS1_HUMAN',
            'sequence_description': 'sp|P86434|AAS1_HUMAN Putative uncharacterized protein ADORA2A-AS1 OS=Homo sapiens GN=ADORA2A-AS1 PE=5 SV=1',
            'sequence': 'MEQDWQPGEEVTPGPEPCSKGQAPLYPIVHVTELKHTDPNFPSNSNAVGTSSGWNRIGTGCSHTWDWRFSCTQQALLPLLGAWEWSIDTEAGGGRREQSQKPCSNGGPAAAGEGRVLPSPCFPWSTCQAAIHKVCRWQGCTRPALLAPSLATLKEHSYP'
        }, {
            'sequence_id': 'sp|Q9UDR5|AASS_HUMAN',
            'sequence_name': 'sp|Q9UDR5|AASS_HUMAN',
            'sequence_description': 'sp|Q9UDR5|AASS_HUMAN Alpha-aminoadipic semialdehyde synthase, mitochondrial OS=Homo sapiens GN=AASS PE=1 SV=1',
            'sequence': 'MLQVHRTGLGRLGVSLSKGLHHKAVLAVRREDVNAWERRAPLAPKHIKGITNLGYKVLIQPSNRRAIHDKDYVKAGGILQEDISEACLILGVKRPPEEKLMSRKTYAFFSHTIKAQEANM'
        }])


class TestConvertStringIdsToBsonObjectIds(unittest.TestCase):

    def test_invalid_list(self):
        string_list = "ASDF"
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

        string_list = 123
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

        string_list = {}
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

        string_list = ()
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_empty_list(self):
        string_list = []
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_string(self):
        string_list = [1]
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

        string_list = [()]
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

        string_list = [{}]
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_valid_list_single_string(self):
        string_list = [
            '589d6d4f35604d2d1c30fbb5'
        ]
        self.assertNotEqual(helpers.convert_string_ids_to_bson_objectids(string_list), False)
        self.assertEquals(len(helpers.convert_string_ids_to_bson_objectids(string_list)), 1)
        self.assertEquals(helpers.convert_string_ids_to_bson_objectids(string_list), [
            ObjectId('589d6d4f35604d2d1c30fbb5'),
        ])

    def test_valid_list_multi_strings(self):
        string_list = [
            '589d6d4f35604d2d1c30fbb5',
            '589d6d4f35604d2d1c30fbb1'
        ]
        self.assertNotEqual(helpers.convert_string_ids_to_bson_objectids(string_list), False)
        self.assertEquals(len(helpers.convert_string_ids_to_bson_objectids(string_list)), 2)
        self.assertEquals(helpers.convert_string_ids_to_bson_objectids(string_list), [
            ObjectId('589d6d4f35604d2d1c30fbb5'),
            ObjectId('589d6d4f35604d2d1c30fbb1')
        ])


class TestAnalyzeSequence(unittest.TestCase):

    def test_invalid_sequence_types(self):
        motif_list = ['[ST]Q']
        motif_frequency = 3
        motif_frame_size = 100

        sequence = ''
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = 123
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = ()
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = []
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = {
            'sequence_id': 0,
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = {
            'sequence_id': '',
            'sequence_name': [],
            'sequence_description': '',
            'sequence': '',
        }
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': {},
            'sequence': '',
        }
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': (),
        }
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_invalid_motif_list_types(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_frequency = 3
        motif_frame_size = 100

        motif_list = ''
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_list = 123
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_list = {}
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_list = ()
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_empty_motif_list(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_frequency = 3
        motif_frame_size = 100

        motif_list = []
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_invalid_motif_list_items(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_frequency = 3
        motif_frame_size = 100

        motif_list = [0]
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_list = [{}]
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_list = [[]]
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_list = [()]
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_invalid_motif_frequency_type(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_list = [
            '[ST]Q',
        ]
        motif_frame_size = 100

        motif_frequency = ''
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frequency = []
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frequency = ()
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frequency = {}
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_invalid_motif_frequency_range(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_list = [
            '[ST]Q',
        ]
        motif_frame_size = 100

        motif_frequency = 1
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frequency = 11
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_invalid_motif_frame_size_type(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_list = [
            '[ST]Q',
        ]
        motif_frequency = 3

        motif_frame_size = ''
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frame_size = []
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frame_size = ()
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frame_size = {}
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_invalid_motif_frame_size_range(self):
        sequence = {
            'sequence_id': '',
            'sequence_name': '',
            'sequence_description': '',
            'sequence': '',
        }
        motif_list = [
            '[ST]Q',
        ]
        motif_frequency = 3

        motif_frame_size = 9
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

        motif_frame_size = 1001
        self.assertFalse(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size))

    def test_valid_analysis_motif_found(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        motif_list = [
            '[ST]Q',
        ]
        motif_frequency = 3
        motif_frame_size = 100

        self.assertNotEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), False)
        self.assertEquals(len(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size)), 2)
        self.assertEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), ([{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }], True))

    def test_valid_analysis_multi_motif_found(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQXZXZXZ'
        }
        motif_list = [
            '[ST]Q',
            '[XY]Z',
        ]
        motif_frequency = 3
        motif_frame_size = 100

        self.assertNotEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), False)
        self.assertEquals(len(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size)), 2)
        self.assertEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), ([{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }, {
            'motif': '[XY]Z',
            'raw_data': [{
                'group': 'XZ',
                'span': (6, 8),
            }, {
                'group': 'XZ',
                'span': (8, 10),
            }, {
                'group': 'XZ',
                'span': (10, 12),
            }],
            'motif_data': [[{
                'group': 'XZ',
                'span': (6, 8),
            }, {
                'group': 'XZ',
                'span': (8, 10),
            }, {
                'group': 'XZ',
                'span': (10, 12),
            }]],
        }], True))

    def test_valid_analysis_multi_motif_found_mixed(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        motif_list = [
            '[ST]Q',
            '[XY]Z',
        ]
        motif_frequency = 3
        motif_frame_size = 100

        self.assertNotEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), False)
        self.assertEquals(len(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size)), 2)
        self.assertEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), ([{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }, {
            'motif': '[XY]Z',
            'raw_data': [],
            'motif_data': [],
        }], True))

    def test_valid_analysis_motif_not_found(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        motif_list = [
            '[XY]Z',
        ]
        motif_frequency = 3
        motif_frame_size = 100

        self.assertNotEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), False)
        self.assertEquals(len(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size)), 2)
        self.assertEquals(helpers.analyze_sequence(sequence, motif_list, motif_frequency, motif_frame_size), ([{
            'motif': '[XY]Z',
            'raw_data': [],
            'motif_data': [],
        }], False))


class TestWriteResultsToCSV(unittest.TestCase):

    def test_invalid_query_type(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]

        query = ''
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = 123
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = []
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = ()
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_invalid_query_contents(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]

        query = {
            'not _id': '',
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_invalid_query_id_type(self):
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]

        query = {
            '_id': '',
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = {
            '_id': 123,
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = {
            '_id': [],
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = {
            '_id': (),
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        query = {
            '_id': {},
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_invalid_sequence_type(self):
        query = {
            '_id': ObjectId(),
        }
        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]

        sequence = ''
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        sequence = 123
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        sequence = []
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        sequence = ()
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_invalid_sequence_data(self):
        query = {
            '_id': ObjectId('589d6d4f35604d2d1c30fbb5'),
        }
        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]

        sequence = {
            'sequence_id': 123,
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        sequence = {
            'sequence_id': '12345',
            'sequence_name': {},
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': (),
            'sequence': 'SQSQSQ'
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': []
        }
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_invalid_analysis_result(self):
        query = {
            '_id': ObjectId('589d6d4f35604d2d1c30fbb5'),
        }
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }

        analysis_result = ''
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = 123
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = {}
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = ()
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_invalid_analysis_result_data(self):
        query = {
            '_id': ObjectId(),
        }
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }

        analysis_result = [{
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': 123,
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': {},
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': (),
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': [],
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': '',
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': 123,
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': {},
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': (),
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'not group': 'SQ',
                'span': (0, 2),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'not span': (0, 2),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': '',
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': 123,
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': {},
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': (),
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'not group': 'SQ',
                'span': (0, 2),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'not span': (0, 2),
            }]],
        }]
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result))

    def test_valid_write_csv_with_file_creation(self):
        query = {
            '_id': ObjectId('589d6d4f35604d2d1c30fbb5'),
            'motifs_as_string': '[ST]Q',
            'motif_frequency': 3,
            'motif_frame_size': 100,
        }
        sequence = {
            'sequence_id': '12345',
            'sequence_name': '12345',
            'sequence_description': '12345',
            'sequence': 'SQSQSQ'
        }
        analysis_result = [{
            'motif': '[ST]Q',
            'raw_data': [{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }],
            'motif_data': [[{
                'group': 'SQ',
                'span': (0, 2),
            }, {
                'group': 'SQ',
                'span': (2, 4),
            }, {
                'group': 'SQ',
                'span': (4, 6),
            }]],
        }]

        csv_filename = ''.join([str(query['_id']), '.csv'])
        csv_file = os.path.join(os.getcwd(), 'downloads', csv_filename)

        # test not false
        self.assertFalse(helpers.write_results_to_csv(query, sequence, analysis_result), False)

        # ensure file doesnt exist
        if pathlib.Path(csv_file).is_file():
            os.remove(csv_file)
        self.assertFalse(pathlib.Path(csv_file).is_file())

        # do csv tests
        helpers.write_results_to_csv(query, sequence, analysis_result)
        self.assertTrue(pathlib.Path(csv_file).is_file())

        # test number of rows
        with open(csv_file, 'r') as fp:
            data = fp.readlines()
        self.assertEqual(len(data), 2)

        # need to test more csv output but its tuff

        # remove when done
        os.remove(csv_file)
        self.assertFalse(pathlib.Path(csv_file).is_file())

if __name__ == '__main__':
    unittest.main()
