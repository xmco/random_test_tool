from unittest import TestCase

from statistical_tests.statistical_tests.linear_complexity_test import LinearComplexityTest


class TestLinearComplexity(TestCase):
    """
    Test of linear complexity algorithm with NIST exemple test case.
    """

    def test_linear_complexity(self):
        with(open("../test_data/e_bin_1000000", "r")) as f:
            chars = f.read()
            lc = LinearComplexityTest()
            self.assertEqual(lc.run_linear_complexity(chars[:-1], 1000), 0.818057422208264)
