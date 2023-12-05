import logging

from scipy.fft import fft
from scipy.special import erfc

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np


@TestRegistry.register("spectral", [DataType.INT, DataType.BITSTRING])
class SpectralTest(StatisticalTest):
    """
    Implementation of spectral test used to detect periods in the sequence.
    Algorithm coming from: https://arxiv.org/pdf/1701.01960.pdf
    """

    def __init__(self):
        super().__init__()
        self.n_values = 0
        self.p_value_limit = 0.05
        self.p_value_limit_strict = 0.01
        self.data_one_minus_one = []
        self.test_output = None
        self.report = None

    def get_data_for_test(self, data):
        """
        Format the data into a bitstring then convert it into a +1/-1 list.
        """
        self.data = data.data
        if data.data_type != DataType.BITSTRING:
            binary_string = self.transform_to_bits()
        else:
            binary_string = self.data
        # For spectral test we want symetric signal over 0 so we replace 0 by -1
        for char in binary_string:
            if char == '0':
                self.data_one_minus_one.append(-1)
            elif char == '1':
                self.data_one_minus_one.append(1)

        self.n_values = len(self.data_one_minus_one)

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Spectral test")

    @staticmethod
    def run_spectral_on_binary(one_minus_one, n_values):
        """
        Launch spectral test on transformed 1 -1 list
        :param one_minus_one: list of -1 and 1
        :param n_values: list length
        :return: p_value
        """
        # Product discrete fourier transform of plus minus one
        s = fft(np.array(one_minus_one))
        modulus = np.abs(s[0:int(n_values / 2)])
        tau = np.sqrt(np.log(1 / 0.05) * n_values)
        # Theoretical number of peaks
        count_n0 = 0.95 * (n_values / 2)
        # Count the number of actual peaks m > T
        count_n1 = len(np.where(modulus < tau)[0])
        # Calculate d and return the p value statistic
        d = (count_n1 - count_n0) / np.sqrt(n_values * 0.95 * 0.05 / 3.8)
        p_val = erfc(abs(d) / np.sqrt(2))
        return p_val

    def run_test(self, data_generator):
        """
        Launch spectral test on the data.
        """
        logging.info("Launching spectral Test")
        self.get_data_for_test(data_generator)
        self.test_output = self.run_spectral_on_binary(self.data_one_minus_one, self.n_values)
        logging.info("Spectral test terminated")
