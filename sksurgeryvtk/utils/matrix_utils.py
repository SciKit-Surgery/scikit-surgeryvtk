# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with matrices.
"""
import vtk
import numpy as np
import sksurgerycore.transforms.matrix as tm


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


def create_matrix_from_list(params):
    """
    Generates a 4x4 numpy ndarray from a list of
    rx,ry,rz,tx,ty,tz in degrees, millimetres.
    :param params list of exactly 6 numbers.
    """
    if len(params) != 6:
        raise ValueError("Incorrect list size:" + str(params))

    rot = tm.construct_rotm_from_euler(params[0],
                                       params[1],
                                       params[2],
                                       sequence='yxz',
                                       is_in_radians=False
                                       )
    trans = np.ndarray((3, 1))
    trans[0] = params[3]
    trans[1] = params[4]
    trans[2] = params[5]
    mat = tm.construct_rigid_transformation(rot, trans)
    return mat


def create_matrix_from_string(parameter_string):
    """
    Generates a 4x4 numpy ndarray from a comma separated
    string of the format rx,ry,rz,tx,ty,tz in degrees, millimetres.

    :param parameter_string: rx,ry,rz,tx,ty,tz in degrees/millimetres
    :return: 4x4 rigid body transform
    """
    params = parameter_string.split(',')
    if len(params) != 6:
        raise ValueError("Incorrect extrinsic:" + parameter_string)

    param_list = [float(params[0]),
                  float(params[1]),
                  float(params[2]),
                  float(params[3]),
                  float(params[4]),
                  float(params[5])
                  ]

    return create_matrix_from_list(param_list)
