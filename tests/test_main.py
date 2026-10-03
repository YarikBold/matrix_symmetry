import unittest

from src.main import is_symmetric


class TestIsSymmetric(unittest.TestCase):
    def test_symmetric_matrix(self):
        matrix = [
            [1, 2],
            [2, 3],
        ]
        self.assertTrue(is_symmetric(matrix))

    def test_non_symmetric_matrix(self):
        matrix = [
            [1, 2],
            [3, 4],
        ]
        self.assertFalse(is_symmetric(matrix))

    def test_single_element_matrix(self):
        matrix = [[5]]
        self.assertTrue(is_symmetric(matrix))

    def test_symmetric_float_matrix(self):
        matrix = [
            [1.5, 2.7],
            [2.7, -3.2],
        ]
        self.assertTrue(is_symmetric(matrix))

    def test_zero_matrix(self):
        matrix = [
            [0, 0],
            [0, 0],
        ]
        self.assertTrue(is_symmetric(matrix))


if __name__ == "__main__":
    unittest.main()
