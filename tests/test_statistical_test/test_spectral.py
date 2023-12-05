from unittest import TestCase

from statistical_tests.statistical_tests.spectral_test import SpectralTest


class TestSpectralTestCase(TestCase):

    def test_spectral_test(self):
        """
        Test of spectral test algorithm with NIST exemple test case.
        """

        st = SpectralTest()

        binary_string = "1100100100001111110110101010001000100001011010001" \
                        "100001000110100110001001100011001100010100010111000"
        data_minus_one = []

        for char in binary_string:
            if char == '0':
                data_minus_one.append(-1)
            elif char == '1':
                data_minus_one.append(1)

        print(st.run_spectral_on_binary(data_minus_one, len(binary_string)))