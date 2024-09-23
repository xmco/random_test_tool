from unittest import TestCase

from statistical_tests.statistical_tests.spectral_test import SpectralTest
from tests.utils import generate_periodic_sequence


class TestSpectralTestCase(TestCase):

    @staticmethod
    def binary_str_to_list(binary_string):
        data_minus_one = []
        for char in binary_string:
            if char == '0':
                data_minus_one.append(-1)
            elif char == '1':
                data_minus_one.append(1)

        return data_minus_one

    def test_spectral_random(self):
        """
        Test of spectral test on e binary expansion.
        """
        with(open("../test_data/e_binary_extention", "r")) as f:
            chars = f.read()
            st = SpectralTest()

            data_minus_one = self.binary_str_to_list(chars)

            self.assertGreater(st.run_spectral_on_binary(data_minus_one, len(data_minus_one)), 0.01)

    def test_spectral_non_random(self):
        """
        Test of spectral  test on non random data.
        """
        chars = generate_periodic_sequence(100000, 64)
        st = SpectralTest()

        data_minus_one = self.binary_str_to_list(chars)
        self.assertGreater(0.01, st.run_spectral_on_binary(data_minus_one, len(data_minus_one)))