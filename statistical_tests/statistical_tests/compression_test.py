import itertools
import logging
import math

from scipy.fft import fft
from scipy.special import erfc

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np

# [n, L, Q = 2 * 10^L, expectedValue, variance]
# Data coming from https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-22r1a.pdf
COMPRESSION_DATA = [
    [387840, 6, 640, 5.2177052, 2.954],
    [904960, 7, 1280, 6.1962507, 3.125],
    [2068480, 8, 2560, 7.1836656, 3.238],
    [4654080, 9, 5120, 8.1764248, 3.311],
    [10342400, 10, 10240, 9.1723243, 3.35],
    [22753280, 11, 20480, 10.170032, 3.384],
    [49643520, 12, 40960, 11.168765, 3.401],
    [107560960, 13, 81920, 12.168070, 3.410],
    [231669760, 14, 163840, 13.167693, 3.416],
    [496435200, 15, 327680, 14.167488, 3.419],
    [1059061760, 16, 655360, 15.167379, 3.421]
]


@TestRegistry.register("compression", [DataType.INT, DataType.BITSTRING])
class CompressionTest(StatisticalTest):
    """
    Compression test implementation.
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
       Format the data into a bitstring
        """
        self.data = data.data
        if data.data_type != DataType.BITSTRING:
            binary_string = self.transform_to_bits()
        else:
            binary_string = self.data

        self.n_values = len(binary_string)
        self.data = binary_string

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Compression test.")

    def backtrack(self, key, L, table):
        """
        Recursive function used to fill the initialisation table.
        """
        if len(key) < L:
            self.backtrack(key + "0", L, table)
            self.backtrack(key + "1", L, table)
        else:
            table[key] = 0

    def run_compression(self, data, n_values):
        """
        Run compression test on a bitstring.
        Implementation inspired from:
        https://github.com/alexandru-stancioiu/Maurer-s-Universal-Statistical-Test/blob/master/maurer.py
        :param data: bitstring
        :param n_values: list_length
        :return: p_value
        """
        # Constants definition
        L = 0  # Length of a block
        Q = 0  # Number of blocks in init sequence
        K = 0  # Number of blocks in test sequence
        expected_value = 0
        variance = 0
        for i, line in enumerate(COMPRESSION_DATA):
            if n_values <= line[0]:
                # we use previous line unless it is the first
                used_line = COMPRESSION_DATA[i - 1] if i - 1 >= 0 else line
                L = used_line[1]
                Q = used_line[2]
                K = int(used_line[0] / L) - Q
                expected_value = used_line[3]
                variance = used_line[4]
                break

        # First we get init and test sequences
        init = data[0:Q * L]
        test = data[Q * L: (Q + K) * L]

        dist_table = {}
        self.backtrack("", L, dist_table)

        for i in range((Q - 1) * L, -1, -L):
            block_id = i / L + 1
            block = str(init[i: i + L])
            if dist_table[block] < block_id:
                dist_table[block] = block_id

        stat_sum = 0
        for i in range(0, K * L, L):
            block_id = Q + i / L + 1
            block = str(test[i: i + L])
            diff = block_id - dist_table[block]
            stat_sum += math.log(diff, 2)
            dist_table[block] = block_id

        fn = stat_sum / K

        c = 0.7 - 0.8 / L + (4 + 32 / L) * math.pow(K, -3 / L) / 15
        sigma = c * math.sqrt(variance / K)
        p_value = math.erfc(math.fabs((fn - expected_value) / (math.sqrt(2) * sigma)))

        return p_value

    def run_test(self, data_generator):
        """
        Launch compression tets on the data.
        """
        logging.info("Launching compression Test")
        self.get_data_for_test(data_generator)
        self.test_output = self.run_compression(self.data, self.n_values)
        logging.info("Compression test terminated")
