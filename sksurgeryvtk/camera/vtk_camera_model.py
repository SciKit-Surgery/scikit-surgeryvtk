# -*- coding: utf-8 -*-

"""
Functions to provide vtkCamera functionality.
"""

import vtk
import numpy as np

def create_vtk_matrix_4x4_from_numpy(array):
    """ Return a new vtkMatrix4x4 from a numpy array. """

    if array.shape != (4, 4):
        raise ValueError('Input array should be a 4x4 matrix')

    vtk_matrix = vtk.vtkMatrix4x4()
    vtk_matrix.DeepCopy(array.ravel())

    return vtk_matrix


def set_projection_matrix(vtk_camera, vtk_matrix):
    """ Enable and Set the ProjectionTransformMatrix for a vtk camera. """

    if not isinstance(vtk_camera, vtk.vtkCamera):
        raise TypeError('Invalid camera object passed')

    if not isinstance(vtk_matrix, vtk.vtkMatrix4x4):
        raise TypeError('Invalid matrix object passed')

    vtk_camera.UseExplicitProjectionTransformMatrixOn()
    vtk_camera.SetExplicitProjectionTransformMatrix(vtk_matrix)


def get_projection_matrix_from_intrinsics(vtk_camera, width, height, near, far):

    aspect = width/height
    vtk_matrix = vtk_camera.GetProjectionTransformMatrix(aspect, near, far)
    print(vtk_matrix)
    np_matrix = np.zeros((4,4))

    for i in range(4):
        for j in range(4):
            np_matrix[i,j] = vtk_matrix.GetElement(i,j)

    print(np_matrix)
    return np_matrix


