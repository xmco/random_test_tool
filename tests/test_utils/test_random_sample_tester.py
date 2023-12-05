from unittest import TestCase

from random_sample_tester.random_sample_tester import RandomSampleTester, RandomSample
from utils.data_type import DataType


class TestRandomSample(TestCase):

    def test_get_data(self):
        """
        Test the get_data function.
        """
        rs = RandomSample()

        rs.get_data("../test_data/int_sep.txt", "int", ",")

        self.assertTrue(rs.data.data)
        self.assertEqual(rs.data.data_type, DataType.INT)