from unittest import TestCase

from statistical_tests.statistical_tests.linear_complexity_test import LinearComplexityTest
from tests.utils import generate_periodic_sequence


class TestLinearComplexity(TestCase):
    """
    Test of linear complexity algorithm.
    """

    def test_linear_complexity(self):
        """
        Test with Nist exemple test case.
        """
        with(open("tests/test_data/e_bin_1000000", "r")) as f:
            chars = f.read()
            lc = LinearComplexityTest()
            self.assertEqual(lc.run_linear_complexity(chars[:-1], 1000), 0.8262011730404891)

    def test_linear_complexity_non_random(self):
        chars = generate_periodic_sequence(100000, 64)
        lc = LinearComplexityTest()
        self.assertGreater(0.01, lc.run_linear_complexity(chars, 1000))
