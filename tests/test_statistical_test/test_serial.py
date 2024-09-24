from unittest import TestCase

from statistical_tests.statistical_tests.serial_test import SerialTest
from tests.utils import generate_unbalanced_sequence
from utils.data_type import DataType


class TestSerial(TestCase):
    """
    Tests on serial algorithm.
    """

    class MockData:
        def __init__(self, data):
            self.data = data
            self.data_type = DataType.BITSTRING

    def test_succes(self):
        """
        Test on e binary expansion.
        """
        with(open("../test_data/e_binary_extention", "r")) as f:
            data = self.MockData(f.read())
            serial = SerialTest()
            serial.run_test(data)
            self.assertGreater(serial.test_output, 0.01)

    def test_failure(self):
        """
        Test on non random data.
        """
        chars = generate_unbalanced_sequence(100000, 0.7)
        data = self.MockData(chars)
        serial = SerialTest()
        serial.run_test(data)
        self.assertGreater(0.01, serial.test_output)

