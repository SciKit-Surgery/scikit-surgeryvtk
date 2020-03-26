import pytest
import numpy as np
import sksurgeryvtk.utils.matrix_utils as mu

def test_get_l2r_matrix_smartliver_format():
    
    l2r = np.array([[1, 2, 3, 1],
                    [4, 5, 6, 2],
                    [7, 8, 9, 3],
                    [0, 0, 0, 1]])

    l2r_smartliver = \
        mu.get_l2r_smartliver_format(l2r)

    expected = np.array([[1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9],
                         [1, 2, 3]])

    assert(np.array_equal(l2r_smartliver, expected))

