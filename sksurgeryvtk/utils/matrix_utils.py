# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with matrices.
"""
import vtk
import numpy as np


def create_vtk_matrix_from_numpy(array):
    """
    Return a new vtkMatrix4x4 from a numpy array.
    """
    if not isinstance(array, np.ndarray):
        raise TypeError('Invalid array object passed')

    if array.shape != (4, 4):
        raise ValueError('Input array should be a 4x4 matrix')

    vtk_matrix = vtk.vtkMatrix4x4()
    vtk_matrix.DeepCopy(array.ravel())

    return vtk_matrix


def validate_vtk_matrix_4x4(matrix):
    """
    Checks that a matrix is a vtkMatrix4x4.
    :param matrix: vtkMatrix4x4
    :raises TypeError
    :return: True
    """
    if not isinstance(matrix, vtk.vtkMatrix4x4):
        raise TypeError('Invalid matrix object passed')
