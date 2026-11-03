"""Тестовый драйвер вычислительного модуля."""

import unittest

from src.processing_module import is_symmetric


class TestProcessing(unittest.TestCase):
    def test_valid_matrices(self):
        cases = [
            ("symmetric", [[1, 2], [2, 3]], True),
            ("non_symmetric", [[1, 2], [3, 4]], False),
            ("single", [[5]], True),
            ("float", [[1.5, 2.7], [2.7, -3.2]], True),
            ("zero", [[0, 0], [0, 0]], True),
        ]
        for name, matrix, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(is_symmetric(matrix), expected)

    def test_invalid_matrices(self):
        cases = [
            ("empty", []),
            ("non_square", [[1, 2]]),
            ("text", [["abc"]]),
            ("infinity", [[float("inf")]]),
        ]
        for name, matrix in cases:
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    is_symmetric(matrix)


if __name__ == "__main__":
    unittest.main()
