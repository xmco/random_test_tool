import logging

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np
from scipy.stats import chisquare


@TestRegistry.register("chi2", [DataType.INT, DataType.BITSTRING, DataType.BYTES])
class Chi2Test(StatisticalTest):
    """
    Implementation of the chi 2 test verifying the uniformity of the distribution on the sample.
    """

    def __init__(self, display_name="Chi2", p_value_limit=0.05, p_value_limit_strict=0.01):
        super().__init__(p_value_limit=p_value_limit, p_value_limit_strict=p_value_limit_strict)
        self.display_name = display_name

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
        return self.generate_test_report(self.display_name)

    def run_test(self, data_generator):
        """
        Launch the Chi2 test.
        """
        logging.info("Launching chi2 Test")
        self.get_data_for_test(data_generator)
        self.test_output = chisquare(self.data).pvalue
        logging.info("Chi2 test terminated")
