from unittest import TestCase

from surfactant_example.utilities import process_variable_name


class TestUtilities(TestCase):

    def test_process_variable_name(self):

        self.assertEqual(
            "should_be_fine",
            process_variable_name("should_be_fine"))

        self.assertEqual(
            "remove_white_space",
            process_variable_name(" remove white space"))

        self.assertEqual(
            "_remove_hyphens",
            process_variable_name("-remove-hyphens"))

        self.assertEqual(
            "remove_hash_symbol",
            process_variable_name("remove hash # symbol"))
