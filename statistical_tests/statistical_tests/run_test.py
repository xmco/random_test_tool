import logging

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
from statsmodels.sandbox.stats.runs import runstest_1samp


@TestRegistry.register("run", [DataType.INT, DataType.BITSTRING])
class RunTest(StatisticalTest):
    """
    Implementation of the run test checking the repartition of increasing and decreasing sequences.
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
        return self.generate_test_report("Run test")

    def run_test(self, data_generator):
        """
        Launch run test on the data.
        """
        logging.info("Launching run Test")
        self.get_data_for_test(data_generator)
        self.test_output = runstest_1samp(self.data)[1]
        logging.info("Run test terminated")
