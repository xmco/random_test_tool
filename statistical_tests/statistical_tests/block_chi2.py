import logging
import math

import numpy as np
from scipy.stats import chisquare
from scipy.special import gammainc

from statistical_tests.statistical_test import TestRegistry, StatisticalTest
from utils.data_type import DataType


@TestRegistry.register("block_chi2", [DataType.INT, DataType.BITSTRING, DataType.BYTES])
class BlockChi2Test(StatisticalTest):
    """
    Implementation of the block chi 2 test verifying the uniformity of the distribution on the sample for size
    M blocks.
    """

    def __init__(self, display_name="Block Chi2", p_value_limit=0.05, p_value_limit_strict=0.01, block_size=100):
        super().__init__(p_value_limit=p_value_limit, p_value_limit_strict=p_value_limit_strict)
        self.display_name = display_name
        self.block_size = block_size

    def get_data_for_test(self, data):
        """
        Format the data.
        """
        if data.data_type == DataType.BITSTRING:
            self.data = list(map(int, data.data))
        else:
            self.data = data.data
            self.data = list(map(int, self.transform_to_bits()))
        self.n_values = len(self.data)

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report(self.display_name)

    @staticmethod
    def run_block_chi2(data, block_size):
        # get the number fo blocks
        n_blocks = math.floor(len(data) / block_size)
        data = data[:n_blocks * block_size]

        chi2_stats = []
        for i in range(n_blocks):
            block_data = data[i * block_size:(i + 1) * block_size]
            # Compute chi-square for the block
            unique, counts = np.unique(block_data, return_counts=True)
            chi2_stat = chisquare(counts).statistic
            chi2_stats.append(chi2_stat)
        chi2 = sum(chi2_stats)
        return 1 - gammainc(n_blocks/2, chi2/2)

    def run_test(self, data_generator):
        """
        Launch the Chi2 test.
        """
        logging.info("Launching chi2 by block test")
        self.get_data_for_test(data_generator)
        self.test_output = self.run_block_chi2(self.data, block_size=self.block_size)
        logging.info("Chi2 by block test terminated")
