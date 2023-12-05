import logging
import os
from dataclasses import dataclass

from statistical_tests.statistical_test import TestRegistry
from utils.data_type import DataType
from bitstring import BitArray


@dataclass
class DataSample:
    data: list
    data_type: DataType


class RandomSample:
    """
    Class used to retrieve and store data from the game to be tested.
    """

    def __init__(self):
        self.data = None

    @staticmethod
    def transform_bytes_to_bits(in_bytes):
        """
        Transform a string of bytes into a bitstring.
        :param in_bytes: bytes
        :return: string of bits (0 and 1)
        """
        return BitArray(bytes=in_bytes).bin[2:]

    def get_data(self, path, data_code, separator):
        """
        Retrieves the data to test, determines the type and creates a generator for this data
        :param separator: separator for INT data type
        :param data_code: data_type given in argument
        :param path: input file paths
        """
        if not os.path.exists(path):
            logging.error(f"The {path} file given as input does not exist. End of execution.")
            raise FileNotFoundError

        data_values = []

        # We determine data type
        data_type = DataType.get_data_type(data_code)

        if data_type == DataType.BYTES:
            with open(path, 'rb') as file:
                # Bytes must be converted into bitstring
                data = file.read()
                data_values = self.transform_bytes_to_bits(data)
                data_type = DataType.BITSTRING
        else:
            with open(path, 'r') as file:
                lines = file.read().splitlines()

                # Processing file
                if data_type == DataType.BITSTRING:
                    data_values = lines[0]

                if data_type == DataType.INT:
                    if separator == "\\n":
                        for line in lines:
                            data_values.append(int(line))
                    else:
                        data_values = list(map(int, lines[0].split(separator)))

        self.data = DataSample(data_values, data_type)


class RandomSampleTester(RandomSample):
    """
    Class used to run statistical statistical_tests and generate the output report.
    """

    def __init__(self):
        super().__init__()
        self.statistical_tests = []
        self.test_results = []

    def _run_test_on_sample(self, data_list, progress_queue):

        for test in self.statistical_tests:
            test.run_test(data_list)
            progress_queue.put(1)

        for test in self.statistical_tests:
            self.test_results.append(test.generate_report())

    def register_tests_for_run(self, test_names):
        """
        Retrieves and configures the statistical_tests to run for this run.
        """
        test_dic = TestRegistry.get_available_tests()
        data_type = self.data.data_type

        if test_names == "all":
            for test in test_dic.items():
                if data_type in test[1][1]:
                    logging.info(f"Adding {test[0]} to the run.")
                    self.statistical_tests.append(test[1][0]())
        else:
            for test_name in test_names:
                if test_name in list(test_dic.keys()):
                    test = test_dic[test_name]
                    if data_type in test[1]:
                        logging.info(f"Adding {test_name} to the run.")
                        self.statistical_tests.append(test[0]())
                else:
                    logging.warning(f"Test {test_name} does not exists.")

    def run_tests(self, progress_queue):
        """
        Runs all statistical_tests configured for this run.
        :param progress_queue: track the number of tests
        """
        logging.info("Launching statistical_tests")
        self._run_test_on_sample(self.data, progress_queue)

