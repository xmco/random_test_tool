from unittest import TestCase

import numpy as np
from scipy.stats import chisquare

from tests.utils import generate_unbalanced_sequence


class TestChi2(TestCase):
    """
    Tests on Chi2 algorithm.
    """

    def test_succes(self):
        """
        Test on e binary expansion.
        """
        with(open("../test_data/e_binary_extention", "r")) as f:
            chars = f.read()
            unique, counts = np.unique(list(map(int, chars)), return_counts=True)
            self.assertGreater(chisquare(counts).pvalue, 0.01)

    def test_failure(self):
        """
        Test on non random data.
        """
        chars = generate_unbalanced_sequence(100000, 0.6)
        unique, counts = np.unique(list(map(int, chars)), return_counts=True)
        self.assertGreater(0.01, chisquare(counts).pvalue)
