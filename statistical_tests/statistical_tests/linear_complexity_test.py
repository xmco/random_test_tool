import copy
import logging

from scipy.special import gammaincc

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np


def berlekamp_massey_algorithm(block_data):
    """
    An implementation of the Berlekamp Massey Algorithm. Taken from Wikipedia [1]
    [1] - https://en.wikipedia.org/wiki/Berlekamp-Massey_algorithm
    The Berlekamp–Massey algorithm is an algorithm that will find the shortest linear feedback shift register (LFSR)
    for a given binary output sequence. The algorithm will also find the minimal polynomial of a linearly recurrent
    sequence in an arbitrary field. The field requirement means that the Berlekamp–Massey algorithm requires all
    non-zero elements to have a multiplicative inverse.
    :param block_data: bitstring
    :return:
    """
    n = len(block_data)
    c = np.zeros(n)
    b = np.zeros(n)
    c[0], b[0] = 1, 1
    l_len, m = 0, 1
    int_data = [int(el) for el in block_data]
    for i in range(n):
        v = int_data[(i - l_len):i]
        v = v[::-1]
        cc = c[1:l_len + 1]
        d = (int_data[i] + np.dot(v, cc)) % 2
        if d == 1:
            temp = copy.copy(c)
            p = np.zeros(n)
            for j in range(0, l_len):
                if b[j] == 1:
                    p[j + i - m] = 1
            c = (c + p) % 2
            if l_len <= 0.5 * i:
                l_len = i + 1 - l_len
                m = i
                b = temp
    return l_len


@TestRegistry.register("linear_complexity", [DataType.INT, DataType.BITSTRING])
class LinearComplexityTest(StatisticalTest):
    """
    Implementation of linear complexity test in python.
    """

    def __init__(self):
        super().__init__()
        self.n_values = 0
        self.p_value_limit = 0.05
        self.p_value_limit_strict = 0.01
        self.test_output = None
        self.report = None

    def get_data_for_test(self, data):
        """
        Format the data into a bitstring.
        """
        self.data = data.data
        if data.data_type != DataType.BITSTRING:
            self.data = self.transform_to_bits()
        self.n_values = len(self.data)

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Linear complexity test")

    @staticmethod
    def run_linear_complexity(data, block_size):
        """
        Implementation of the linear complexity test.
        Algorithm adapted from https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-22r1a.pdf 2.10.4
        :param data: bitstring
        :param block_size: size of the blocks where lsfr is calculated
        :return: p-value
        """
        # Degree of freedom and theoric probabilities
        dof = 6
        peaks = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]

        t2 = (block_size / 3.0 + 2.0 / 9) / 2 ** block_size
        mean = 0.5 * block_size + (1.0 / 36) * (9 + (-1) ** (block_size + 1)) - t2

        num_blocks = int(len(data) / block_size)
        if num_blocks > 1:
            block_end = block_size
            block_start = 0
            blocks = []
            for i in range(num_blocks):
                blocks.append(data[block_start:block_end])
                block_start += block_size
                block_end += block_size

            complexities = []
            for block in blocks:
                complexities.append(berlekamp_massey_algorithm(block))

            t = ([(((-1) ** block_size) * (chunk - mean) + 2.0 / 9) for chunk in complexities])
            vg = np.histogram(t, bins=[-9999999999, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 9999999999])[0]
            im = ([((vg[ii] - num_blocks * peaks[ii]) ** 2) / (num_blocks * peaks[ii]) for ii in range(7)])

            chi_squared = 0.0
            for i in range(len(peaks)):
                chi_squared += im[i]
            p_val = gammaincc(dof / 2.0, chi_squared / 2.0)
            return p_val

    def run_test(self, data_generator, block_size=1000):
        """
        Launch linear complexity test on the data.
        """
        logging.info("Launching linear complexity Test")
        self.get_data_for_test(data_generator)
        p_val = self.run_linear_complexity(self.data, block_size)
        self.test_output = p_val
        logging.info("Linear complexity terminated")
