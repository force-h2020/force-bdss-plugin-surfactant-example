import re

import numpy as np


def remove_digits(string):
    """Removes digits from a string"""
    return re.sub(r"\d+", "", string)


def numpy_count(array, value):
    """Counts the number of occurrences of value in array"""
    return np.sum(array == value)


def matrix_threshold(matrix, upper_thresh=1, lower_thresh=0):
    """Return mask corresponding to elements of matrix that
    lie between the lower and upper threshold values"""

    mask = np.where(matrix < upper_thresh, 1, 0)
    mask = np.where(matrix > lower_thresh, mask, 0)

    return mask


def block_matrix(matrix, block_shape=(1, 1)):
    """Reshapes a matrix into a grid of smaller 'block' matrices of
    shape block_shape. Performs this operation in place,
    thereby saving a lot of speed and memory

    Parameters
    ----------
    matrix: array_like of float
        A 2D array to reshape into a block grid
    block_shape: tuple of int:
        Shape of each block in grid along each axis
    """

    # Record original matrix shape and calculate number of blocks
    # along each axis
    matrix_shape = matrix.shape
    n_blocks = [matrix_shape[i] // block_shape[i] for i in range(2)]

    assert n_blocks[0] * block_shape[0] == matrix_shape[0]
    assert n_blocks[1] * block_shape[1] == matrix_shape[1]

    # This tracer keeps track of each block, so we can use it to rearrange
    # back into the original matrix order
    tracer = np.arange(n_blocks[0] * n_blocks[1])
    tracer = tracer.reshape(n_blocks[0], n_blocks[1])

    # Numpy reshape operation collects rows, so we need to manipulate
    # this in order to reshape both rows and columns of matrix into
    # a grid
    matrix = matrix.reshape(matrix_shape[0],
                            n_blocks[1], block_shape[1])

    matrix = np.rot90(matrix).reshape(matrix_shape)
    tracer = np.rot90(tracer)

    matrix = matrix.reshape(n_blocks[0] * n_blocks[1],
                            block_shape[0], block_shape[1])
    tracer = tracer.reshape(n_blocks[0] * n_blocks[1])

    # After getting the matrix into the correct rearrangement, we now
    # need to arrange it into the correct order again
    matrix = matrix[np.argsort(tracer)]
    matrix = matrix.reshape(n_blocks[0], n_blocks[1],
                            block_shape[0], block_shape[1])

    return matrix


def block_diagonal(matrix, size=1, value=1):
    """Sets the elements inside of a series of blocks of size x size along
     the matrix diagonal to value"""

    n_blocks = matrix.shape[0] // size

    assert matrix.shape[0] == matrix.shape[1]
    assert n_blocks * size == matrix.shape[0]

    for index in range(n_blocks):
        start = index * size
        end = (index + 1) * size
        matrix[start:end, start:end] = value


def sum_filter(matrix, block_shape=(1, 1)):
    """Applies a block filter to matrix that returns the summation
    of all elements in block. Currently only supports 2D arrays"""

    assert matrix.ndim == 2

    # Split up matrix into blocks
    matrix = block_matrix(matrix, block_shape)

    # Sum up all elements inside blocks
    new_matrix = matrix.sum(axis=(-2, -1))

    return new_matrix
