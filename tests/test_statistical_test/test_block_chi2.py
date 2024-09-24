from unittest import TestCase

from statistical_tests.statistical_tests.block_chi2 import BlockChi2Test

from tests.utils import generate_unbalanced_sequence


class TestBlockChi2(TestCase):
    """
    Tests on Block Chi2 algorithm.
    """

    def test_nist(self):
        """
        Test based on the exemple given in https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-22r1a.pdf
        2.2.8
        """
        data = "1100100100001111110110101010001000100001011010001100001000110100110001001100011001100010100010111000"
        numbers = list(map(int, data))
        b_chi2 = BlockChi2Test()
        self.assertEqual(b_chi2.run_block_chi2(numbers, block_size=10), 0.7064384496412806)

    def test_succes(self):
        """
        Test on e binary expansion.
        """
        with(open("../test_data/e_binary_extention", "r")) as f:
            chars = f.read()
            numbers = list(map(int, chars))
            b_chi2 = BlockChi2Test()
            self.assertGreater(b_chi2.run_block_chi2(numbers), 0.01)

    def test_failure(self):
        """
        Test on non random data.
        """
        chars = generate_unbalanced_sequence(100000, 0.9)
        numbers = list(map(int, chars))
        b_chi2 = BlockChi2Test()
        self.assertGreater(0.01, b_chi2.run_block_chi2(numbers))