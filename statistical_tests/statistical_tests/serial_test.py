import logging

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np
from scipy.stats import chisquare


@TestRegistry.register("serial", [DataType.INT, DataType.BITSTRING])
class SerialTest(StatisticalTest):
    """
    Implementation of serial test checking the distribution of pairs of numbers..
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
        Format the test data.
        """
        values = data.data if data.data_type != DataType.BITSTRING else list(map(int, data.data))
        n_unique_values = len(np.unique(values))
        bins = np.zeros((n_unique_values, n_unique_values))
        for idx in range(len(values) - 1):
            bins[values[idx]-1][values[idx+1]-1] += 1
        self.n_values = len(values)

        self.data = bins.flatten()

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Serial test")

    def run_test(self, data_generator):
        """
        Launch serial test on the data.
        """
        logging.info("Launching serial Test")
        self.get_data_for_test(data_generator)
        self.test_output = chisquare(self.data).pvalue
        logging.info("Serial test terminated")
