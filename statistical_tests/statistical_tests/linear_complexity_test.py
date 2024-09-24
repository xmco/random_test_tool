import logging
import berlekamp_messey

from scipy.special import gammaincc

from statistical_tests.statistical_test import StatisticalTest, TestRegistry
from utils.data_type import DataType
import numpy as np


@TestRegistry.register("linear_complexity", [DataType.INT, DataType.BITSTRING, DataType.BYTES])
class LinearComplexityTest(StatisticalTest):
    """
    Implementation of linear complexity test in python.
    """

    def __init__(self, display_name="Linear Complexity", p_value_limit=0.05, p_value_limit_strict=0.01,
                 block_size=1000):
        super().__init__(p_value_limit=p_value_limit, p_value_limit_strict=p_value_limit_strict)
        self.display_name = display_name
        self.block_size = block_size

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
        return self.generate_test_report(self.display_name)

    @staticmethod
    def run_linear_complexity(data, block_size):
        """
        Implementation of the linear complexity test.
        Algorithm adapted from https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-22r1a.pdf 2.10.4
        :param data: bitstring
        :param block_size: size of the blocks where lsfr is calculated
        :return: p-value
        """
        # Degree of freedom and theoric probabilities
        dof = 6
        peaks = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]

        t2 = (block_size / 3.0 + 2.0 / 9) / 2 ** block_size
        mean = 0.5 * block_size + (1.0 / 36) * (9 + (-1) ** (block_size + 1)) - t2

        num_blocks = int(len(data) / block_size)
        if num_blocks > 1:
            block_end = block_size
            block_start = 0
            blocks = []
            for i in range(num_blocks):
                blocks.append(data[block_start:block_end])
                block_start += block_size
                block_end += block_size

            complexities = []
            for block in blocks:
                s = list(map(int, block))
                complexities.append(berlekamp_messey.berlekamp_messey(s, len(s)))

            t = ([(((-1) ** block_size) * (chunk - mean) + 2.0 / 9) for chunk in complexities])
            vg = np.histogram(t, bins=[-9999999999, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 9999999999])[0]
            im = ([((vg[ii] - num_blocks * peaks[ii]) ** 2) / (num_blocks * peaks[ii]) for ii in range(7)])

            chi_squared = 0.0
            for i in range(len(peaks)):
                chi_squared += im[i]
            p_val = gammaincc(dof / 2.0, chi_squared / 2.0)
            return p_val

    def run_test(self, data_generator):
        """
        Launch linear complexity test on the data.
        """
        logging.info("Launching linear complexity Test")
        self.get_data_for_test(data_generator)
        p_val = self.run_linear_complexity(self.data, self.block_size)
        self.test_output = p_val
        logging.info("Linear complexity terminated")
