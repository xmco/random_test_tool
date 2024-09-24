import logging
import math

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np
from scipy.stats import chisquare
from scipy.special import gammainc


@TestRegistry.register("serial", [DataType.INT, DataType.BITSTRING, DataType.BYTES])
class SerialTest(StatisticalTest):
    """
    Implementation of serial test checking the distribution of pairs of numbers.
    """

    def __init__(self, display_name="Serial", p_value_limit=0.05, p_value_limit_strict=0.01, m_sequence=3):
        super().__init__(p_value_limit=p_value_limit, p_value_limit_strict=p_value_limit_strict)
        self.display_name = display_name
        self.m_sequence = m_sequence

    def get_data_for_test(self, data):
        """
        Format the test data.
        """
        if data.data_type != DataType.BITSTRING:
            self.data = data.data
            self.data = self.transform_to_bits()
        else:
            self.data = data.data
        self.n_values = len(self.data)

    def compute_phi_sum(self, m_freq, m_seq):
        phi_sum = 0
        for m_value in m_freq:
            phi_sum += m_value * m_value
        phi_sum = phi_sum * pow(2, m_seq) / self.n_values - self.n_values
        return phi_sum

    def serial_test(self, m_sequence):
        """
        Implementation of the serial test taken from
        http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        """
        # Minimal allowed value for m  is 3
        if m_sequence < 3:
            logging.error("Minimal value for m parameter in serial test is 3")
            raise ValueError

        # First we append m bits to the end of the sequence
        data = self.data + self.data[:(m_sequence - 1)]

        # Then we determine the frequency of all possible m and m+1 bit blocks
        m_bits = np.zeros(int("1" * m_sequence, 2) + 1)
        m_1_bits = np.zeros(int("1" * (m_sequence - 1), 2) + 1)
        m_2_bits = np.zeros(int("1" * (m_sequence - 2), 2) + 1)
        for idx in range(len(data)):
            m_bits[int(data[idx:idx + m_sequence], 2)] += 1
            m_1_bits[int(data[idx:idx + m_sequence - 1], 2)] += 1
            m_2_bits[int(data[idx:idx + m_sequence - 2], 2)] += 1

        # We compute the test statistics
        d_phi = self.compute_phi_sum(m_bits, m_sequence) - self.compute_phi_sum(m_1_bits, m_sequence - 1)
        return 1 - gammainc(pow(2, m_sequence - 2), d_phi/2)

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report(self.display_name)

    def run_test(self, data_generator):
        """
        Launch serial test on the data.
        """
        logging.info("Launching serial Test")
        self.get_data_for_test(data_generator)
        self.test_output = self.serial_test(self.m_sequence)
        logging.info("Serial test terminated")
