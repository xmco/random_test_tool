import logging
import math

import numpy as np
from scipy.special import gammainc

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType


@TestRegistry.register("run_of_ones", [DataType.INT, DataType.BITSTRING, DataType.BYTES])
class LongestRunOfOnes(StatisticalTest):
    """
    Longest run of Ones test, algorithm taken from:
    http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    """

    def __init__(self, display_name="Longest Run of Ones", p_value_limit=0.05, p_value_limit_strict=0.01):
        super().__init__(p_value_limit=p_value_limit, p_value_limit_strict=p_value_limit_strict)
        self.display_name = display_name

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
        return self.generate_test_report(self.display_name)

    @staticmethod
    def get_block_size(data):
        """
        Get block size and expected probabilities based on the input as given in:
        http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        """
        if len(data) < 6272:
            return {
                "K": 3,
                "M": 8,
                "v_i": [1, 2, 3, 4],
                "p_i": [0.2148, 0.3672, 0.2305, 0.1875]
            }
        if len(data) < 75000:
            return {
                "K": 5,
                "M": 128,
                "v_i": [4, 5, 6, 7, 8, 9],
                "p_i": [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
            }
        else:
            return {
                "K": 6,
                "M": 10000,
                "v_i": [10, 11, 12, 13, 14, 15, 16],
                "p_i": [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]
            }

    def longest_run_of_ones(self, data):

        params = self.get_block_size(data)

        # get number of blocks
        n_blocks = math.floor(len(data)/params["M"])
        data = data[:(n_blocks*params["M"])]

        # Get longest run of ones for each block
        bins = np.zeros(params["K"]+1)
        for i in range(n_blocks):
            current_block = data[i*params["M"]:(i+1)*params["M"]]
            one_count = 0
            streak = 0
            for value in current_block:
                if value == "1":
                    one_count += 1
                else:
                    streak = max(one_count, streak)
                    one_count = 0
            streak = max(one_count, streak)
            for v_i, v in enumerate(params["v_i"]):
                if streak <= v:
                    bins[v_i] += 1
                    break
            if streak > params["v_i"][-1]:
                bins[-1] += 1

        # Compute the chi statistic and p-value
        chi_stat = 0
        for i in range(len(bins)):
            chi_stat += (pow(bins[i] - n_blocks*params["p_i"][i], 2) / (n_blocks*params["p_i"][i]))

        return 1 - gammainc(params["K"]/2, chi_stat/2)

    def run_test(self, data_generator):
        """
        Launch longest run of ones tets on the data.
        """
        logging.info("Launching longest run of ones Test")
        self.get_data_for_test(data_generator)
        self.test_output = self.longest_run_of_ones(self.data)
        logging.info("Longest run of ones test terminated")
