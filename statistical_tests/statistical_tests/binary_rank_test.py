import logging
import math

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType


def compute_binary_rank(rows):
    """
    This method calculates the rank of the matrix on the group GL(2) (linear group of order two).
    To do this, we use line elimination operations.
    :param rows: list of integers representing the rows
    :return: rank of the matrix
    """
    rank = 0
    while rows:
        pivot_row = rows.pop()
        if pivot_row:
            rank += 1
            lsb = pivot_row & -pivot_row
            for index, row in enumerate(rows):
                if row & lsb:
                    rows[index] = row ^ pivot_row

    return rank


@TestRegistry.register("binary_matrix", [DataType.INT, DataType.BITSTRING])
class BinaryMatrixTest(StatisticalTest):
    """
    Implementation of the binary matrix test in python.
    Checks the binary rank of matrices formed by substrings of the input compared to the theory.
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
        Format the data into a bitstring.
        """
        self.data = data.data
        if data.data_type != DataType.BITSTRING:
            self.data = self.transform_to_bits()
        self.n_values = len(self.data)

    def generate_report(self):
        """
        Generate a report with correct test_name.
        """
        return self.generate_test_report("Binary rank test")

    @staticmethod
    def run_binary_test(bytestring, matrix_size):
        """
        Binary test algorithm.
        Adapted from https://gist.github.com/StuartGordonReid/885c56037beb8c74b4e8
        """
        n_values = len(bytestring)
        block_size = int(matrix_size * matrix_size)
        num_m = math.floor(n_values / (matrix_size * matrix_size))
        block_start, block_end = 0, block_size

        if num_m > 0:
            max_ranks = [0, 0, 0]
            for im in range(num_m):
                block_data = bytestring[block_start:block_end]
                # We convert the block into a list of integers bas matrix_size
                rows = []
                for i in range(matrix_size):
                    int_data = block_data[i * matrix_size:(i + 1) * matrix_size]
                    int_value = int(int_data, 2)
                    rows.append(int_value)
                # we then compute the rank
                rank = compute_binary_rank(rows.copy())
                if rank == matrix_size:
                    max_ranks[0] += 1
                elif rank == (matrix_size - 1):
                    max_ranks[1] += 1
                else:
                    max_ranks[2] += 1
                # Update index trackers
                block_start += block_size
                block_end += block_size

            peaks = [1.0, 0.0, 0.0]
            for x in range(1, 50):
                peaks[0] *= 1 - (1.0 / (2 ** x))
            peaks[1] = 2 * peaks[0]
            peaks[2] = 1 - peaks[0] - peaks[1]

            chi = 0.0
            for i in range(len(peaks)):
                chi += pow((max_ranks[i] - peaks[i] * num_m), 2.0) / (peaks[i] * num_m)
            p_val = math.exp(-chi / 2)
            return p_val

    def run_test(self, data_generator, matrix_size=32):
        """
        Launch binary rank test on the data.
        """
        logging.info("Launching binary matrix Test")
        self.get_data_for_test(data_generator)
        p_val = self.run_binary_test(self.data, matrix_size)
        self.test_output = p_val
        logging.info("Binary matrix terminated")
