from unittest import TestCase

from statistical_tests.statistical_tests.compression_test import CompressionTest
from tests.utils import generate_periodic_sequence


class TestCompression(TestCase):
    """
    Tests on Compression algorithm.
    """

    def test_succes(self):
        """
        Test on e binary expansion.
        """
        with(open("../test_data/e_bin_1000000", "r")) as f:
            chars = f.read()
            ct = CompressionTest()
            self.assertGreater(ct.run_compression(chars[:-1], len(chars[:-1])), 0.01)

    def test_failure(self):
        """
        Test on non random data.
        """
        chars = generate_periodic_sequence(1000000, 64)
        ct = CompressionTest()
        self.assertGreater(0.01, ct.run_compression(chars, len(chars)))
