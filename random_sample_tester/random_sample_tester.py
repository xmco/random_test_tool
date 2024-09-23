import logging
import os
from dataclasses import dataclass

from statistical_tests.statistical_test import TestRegistry
from utils.data_type import DataType
from bitstring import BitArray

from utils.exceptions import RTTException


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

    def get_data(self, data, data_code, separator, chunks):
        """
        Retrieves the data to test, determines the type and creates a generator for this data
        :param separator: separator for INT data type
        :param data_code: data_type given in argument
        :param chunks whether the chunks option is activated
        :param data: input file paths or DataSample object
        """
        if chunks:
            # Chunk option is activated, data is already in DataSample format
            self.data = data
            return

        if not os.path.exists(data):
            raise RTTException(f"The '{data}' file given as input does not exist.")

        if os.path.isdir(data):
            raise RTTException(f"The '{data}' file given as input is a directory. The input must only contain files")

        data_values = []

        # We determine data type
        data_type = DataType.get_data_type(data_code)

        if data_type == DataType.BYTES:
            with open(data, 'rb') as file:
                # Bytes must be converted into bitstring
                data = file.read()
                data_values = self.transform_bytes_to_bits(data)
                data_type = DataType.BITSTRING
        else:
            with open(data, 'r') as file:
                lines = file.read().splitlines()

                # Processing file
                if data_type == DataType.BITSTRING:
                    data_values = lines[0]

                try:
                    if data_type == DataType.INT:
                        if separator == "\\n":
                            for line in lines:
                                data_values.append(int(line))
                        else:
                            data_values = list(map(int, lines[0].split(separator)))
                except (ValueError, UnicodeDecodeError):
                    raise RTTException("Invalid data type encountered.")

        self.data = DataSample(data_values, data_type)

        if len(self.data.data) < 10000:
            logging.warning(f"Small data length, most tests will not work properly.")


class RandomSampleTester(RandomSample):
    """
    Class used to run statistical_tests and generate the output report.
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

    def register_tests_for_run(self, statistical_tests):
        """
        Retrieves and configures the statistical_tests to run for this run.
        """
        for test in statistical_tests:
            if test.params:
                self.statistical_tests.append(test.test_class(display_name=test.display_name, **test.params))
            else:
                self.statistical_tests.append(test.test_class())

    def run_tests(self, progress_queue):
        """
        Runs all statistical_tests configured for this run.
        :param progress_queue: track the number of tests
        """
        logging.info("Launching statistical_tests")
        self._run_test_on_sample(self.data, progress_queue)

