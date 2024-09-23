from unittest import TestCase

from statistical_tests.statistical_tests.longest_run_of_ones import LongestRunOfOnes

from tests.utils import generate_unbalanced_sequence


class TestLongestRunOfOnes(TestCase):
    """
    Tests on longest run of ones algorithm.
    """

    def test_nist(self):
        """
        Test based on the exemple given in https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-22r1a.pdf
        """
        data = "1100110000010101011011000100110011100000000000100100110101010001000100111101011010000000110101111100" \
               "1100111001101101100010110010"
        longest_runs = LongestRunOfOnes()
        self.assertEqual(longest_runs.longest_run_of_ones(data), 0.1805979767855579)

    def test_succes(self):
        """
        Test on e binary expansion.
        """
        with(open("../test_data/e_binary_extention", "r")) as f:
            chars = f.read()
            longest_runs = LongestRunOfOnes()
            self.assertGreater(longest_runs.longest_run_of_ones(chars), 0.01)

    def test_failure(self):
        """
        Test on non random data.
        """
        chars = generate_unbalanced_sequence(100000, 0.9)
        longest_runs = LongestRunOfOnes()
        self.assertGreater(0.01, longest_runs.longest_run_of_ones(chars))