from unittest import TestCase

import numpy as np

from surfactant_example.micelle.utilities import (
    numpy_count, matrix_threshold, block_diagonal,
    sum_filter, block_matrix, remove_digits
)


def test_block_matrix(matrix, n_blocks):
    """Split a matrix into a list of smaller matrices of
    size n_block x n_block"""

    return np.stack([np.array_split(array, n_blocks[1], axis=1)
                     for array in np.array_split(matrix, n_blocks[0])])


class UtilitiesTestCase(TestCase):

    def setUp(self):
        self.array = np.array([0, 0, 4, 4, 5, 6, 1, 1])

        self.matrix = np.array([[0, 0, 4, 0],
                                [4, 0, 6, 1],
                                [1, 1, 0, 0],
                                [0, 0, 0, 0]])

        self.large_matrix = np.array(
            [[0, 0, 0, 0, 1, 1, 1, 1],
             [0, 0, 0, 0, 1, 1, 1, 1],
             [0, 0, 0, 0, 1, 1, 1, 1],
             [0, 0, 0, 0, 1, 1, 1, 1],
             [2, 2, 2, 2, 3, 3, 3, 3],
             [2, 2, 2, 2, 3, 3, 3, 3],
             [2, 2, 2, 2, 3, 3, 3, 3],
             [2, 2, 2, 2, 3, 3, 3, 3]])

    def test_remove_digits(self):
        string = '4ght6aos57'
        self.assertEqual('ghtaos', remove_digits(string))

    def test_numpy_count(self):

        self.assertEqual(2, numpy_count(self.array, 0))
        self.assertEqual(2, numpy_count(self.array, 1))
        self.assertEqual(2, numpy_count(self.array, 4))
        self.assertEqual(1, numpy_count(self.array, 5))
        self.assertEqual(1, numpy_count(self.array, 6))

    def test_block_matrix(self):

        stack = block_matrix(self.matrix, (2, 2))
        self.assertEqual((2, 2, 2, 2), stack.shape)

        self.assertTrue(
            np.allclose(
                np.array([[0, 0], [4, 0]]), stack[0][0])
        )
        self.assertTrue(
            np.allclose(
                np.array([[4, 0], [6, 1]]), stack[0][1])
        )
        self.assertTrue(
            np.allclose(
                np.array([[1, 1], [0, 0]]), stack[1][0])
        )
        self.assertTrue(
            np.allclose(
                np.array([[0, 0], [0, 0]]), stack[1][1])
        )

        stack = block_matrix(self.large_matrix, (2, 2))
        self.assertEqual((4, 4, 2, 2), stack.shape)
        self.assertTrue(
            np.allclose(
                stack,
                test_block_matrix(self.large_matrix, [4, 4])
            )
        )

        stack = block_matrix(self.matrix, (2, 2))
        self.assertEqual((2, 2, 2, 2), stack.shape)
        self.assertTrue(
            np.allclose(
                test_block_matrix(self.matrix, [2, 2]), stack)
        )

        stack = block_matrix(self.large_matrix, (4, 2))
        self.assertEqual((2, 4, 4, 2), stack.shape)
        self.assertTrue(
            np.allclose(
                test_block_matrix(self.large_matrix, [2, 4]), stack)
        )

    def test_block_diagonal(self):

        matrix = np.zeros((4, 4))
        block_diagonal(matrix)

        self.assertTrue(
            np.allclose(
                np.identity(4),
                matrix
            )
        )

        block_diagonal(matrix, size=2)

        self.assertTrue(
            np.allclose(
                np.array([[1, 1, 0, 0],
                          [1, 1, 0, 0],
                          [0, 0, 1, 1],
                          [0, 0, 1, 1]]),
                matrix
            )
        )

        with self.assertRaises(AssertionError):
            block_diagonal(matrix, size=3)

    def test_sum_filter(self):

        self.assertTrue(
            np.allclose(
                np.array([[4, 11],
                          [2, 0]]),
                sum_filter(self.matrix, block_shape=(2, 2))
            )
        )

        with self.assertRaises(AssertionError):
            sum_filter(self.matrix, block_shape=(3, 2))

        matrix = np.array([[0, 1, 1, 0, 0, 0],
                           [1, 0, 1, 0, 0, 0],
                           [1, 1, 0, 0, 1, 1],
                           [0, 0, 0, 0, 1, 1],
                           [0, 0, 1, 1, 0, 1],
                           [0, 0, 1, 1, 1, 0]])

        self.assertTrue(
            np.allclose(
                np.array([[6, 2],
                          [2, 6]]),
                sum_filter(matrix, block_shape=(3, 3))
            )
        )

        large_matrix = np.array(
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
             [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
             [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

        self.assertTrue(
            np.allclose(
                np.array([[0, 1, 1, 2],
                          [1, 2, 1, 0],
                          [1, 1, 2, 3],
                          [2, 0, 3, 0]]),
                sum_filter(large_matrix, block_shape=(3, 3))
            )
        )

    def test_matrix_filter(self):

        filter = matrix_threshold(self.matrix, 0)
        self.assertEqual(0, np.triu(filter).sum())

        filter = matrix_threshold(self.matrix, 1.1)
        self.assertEqual(3, np.count_nonzero(filter))
        self.assertEqual(1, filter[2][0])
        self.assertEqual(1, filter[2][1])
        self.assertEqual(1, filter[1][3])

        filter = matrix_threshold(self.matrix, 4.1)
        self.assertEqual(5, np.count_nonzero(filter))
        self.assertEqual(1, filter[2][0])
        self.assertEqual(1, filter[2][1])
        self.assertEqual(1, filter[1][3])
        self.assertEqual(1, filter[0][2])
        self.assertEqual(1, filter[1][0])

        filter = matrix_threshold(self.matrix, 6.1)
        self.assertEqual(6, np.count_nonzero(filter))
        self.assertEqual(1, filter[2][0])
        self.assertEqual(1, filter[2][1])
        self.assertEqual(1, filter[1][3])
        self.assertEqual(1, filter[0][2])
        self.assertEqual(1, filter[1][0])
        self.assertEqual(1, filter[1][2])
