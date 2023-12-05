import logging

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np
from scipy.stats import chisquare


@TestRegistry.register("chi2", [DataType.INT, DataType.BITSTRING])
class Chi2Test(StatisticalTest):
    """
    Implementation of the chi 2 test verifying the uniformity of the distribution on the sample.
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
        Format the data.
        """
        if data.data_type == DataType.BITSTRING:
            numbers = list(map(int, data.data))
        else:
            numbers = data.data
        unique, counts = np.unique(numbers, return_counts=True)
        self.n_values = len(numbers)

        self.data = counts

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Chi-square goodness of fit")

    def run_test(self, data_generator):
        """
        Launch the Chi2 test.
        """
        logging.info("Launching chi2 Test")
        self.get_data_for_test(data_generator)
        self.test_output = chisquare(self.data).pvalue
        logging.info("Chi2 test terminated")
