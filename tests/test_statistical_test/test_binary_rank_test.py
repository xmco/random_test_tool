from unittest import TestCase

from statistical_tests.statistical_tests.binary_rank_test import compute_binary_rank, BinaryMatrixTest


class TestRankComputation(TestCase):
    """
    Test of matrix rank calculation.
    """

    def test_matrix_rank_2(self):
        """
        Test with rank equals to 2:
        0 1 0
        1 1 0
        0 1 0
        """
        # Matrix written with rows as integers
        matrix = [2, 4, 2]
        self.assertEqual(compute_binary_rank(matrix), 2)

    def test_matrix_rank_3(self):
        """
        Test with rank equals to 3:
        0 1 0
        1 0 1
        0 1 1
        """
        # Matrix written with rows as integers
        matrix = [2, 5, 3]
        self.assertEqual(compute_binary_rank(matrix), 3)

    def test_matrix_rank_4(self):
        """
        Test with rank equals to 4:
        1 0 0 0 0 0
        0 0 0 0 0 1
        1 0 0 0 0 1
        1 0 1 0 1 0
        0 0 1 0 1 1
        0 0 0 0 1 0
        """
        # Matrix written with rows as integers
        matrix = [32, 1, 33, 42, 11, 2]
        self.assertEqual(compute_binary_rank(matrix), 4)


class TestBinaryMatrix(TestCase):
    """
    Test of binary matrix algorithm with NIST exemple test case.
    """

    def test_binary_matrix(self):

        with(open("../test_data/e_binary_extention", "r")) as f:
            chars = f.read()
            bm = BinaryMatrixTest()
            self.assertEqual(bm.run_binary_test(chars[:-1], 32), 0.5320686217466569)




