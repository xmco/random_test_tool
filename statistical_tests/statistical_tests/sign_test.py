import logging

import numpy as np

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
from statsmodels.stats.descriptivestats import sign_test


@TestRegistry.register("sign", [DataType.INT, DataType.BITSTRING])
class SignTest(StatisticalTest):
    """
    Implementation of the sign test that checks the equal repartition of the data around the median.
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
        Format the data for the test.
        """

        if data.data_type == DataType.BITSTRING:
            self.data = list(map(int, data.data))
        else:
            self.data = data.data
        self.n_values = len(self.data)

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Sign test")

    def run_test(self, data_generator):
        """
        Launch sign test on the data.
        """
        logging.info("Launching sign Test")
        self.get_data_for_test(data_generator)
        possible_values = np.unique(self.data)
        self.test_output = sign_test(self.data,  np.median(possible_values))[1]
        logging.info("Sign test terminated")
