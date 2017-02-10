import unittest
import helpers

from bson import ObjectId


class TestFormatTextareaText(unittest.TestCase):
    def test_invalid_input_text_type(self):
        input_text = 123
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

    def test_invalid_input_text_type_2(self):
        input_text = True
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

    def test_invalid_input_text_type_3(self):
        input_text = []
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

    def test_invalid_input_text_type_4(self):
        input_text = {}
        self.assertFalse(helpers.format_textarea_text_fasta(input_text))

    def test_invalid_input_text_type_5(self):
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


class TestConvertStringIdsToBsonObjectIds(unittest.TestCase):

    def test_invalid_list_1(self):
        string_list = "ASDF"
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_2(self):
        string_list = 123
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_3(self):
        string_list = {}
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_4(self):
        string_list = ()
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_empty_list(self):
        string_list = []
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_string_1(self):
        string_list = [1]
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_string_2(self):
        string_list = [()]
        self.assertFalse(helpers.convert_string_ids_to_bson_objectids(string_list))

    def test_invalid_list_string_3(self):
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



if __name__ == '__main__':
    unittest.main()
