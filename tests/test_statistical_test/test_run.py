from unittest import TestCase

from statsmodels.sandbox.stats.runs import runstest_1samp
from tests.utils import generate_periodic_sequence


class TestRun(TestCase):
    """
    Tests on Run algorithm.
    """

    def test_succes(self):
        """
        Test on e binary expansion.
        """
        with(open("../test_data/e_binary_extention", "r")) as f:
            chars = f.read()
            data = list(map(int, chars))
            self.assertGreater(runstest_1samp(data)[1], 0.01)

    def test_failure(self):
        """
        Test on non random data.
        """
        chars = generate_periodic_sequence(100000, 64)
        data = list(map(int, chars))
        self.assertGreater(0.01, runstest_1samp(data)[1])
