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


def create_numpy_matrix_from_vtk(matrix):
    """
    Returns a new numpy 4x4 matrix from a vtkMatrix4x4.
    """
    validate_vtk_matrix_4x4(matrix)

    transformation = np.eye(4)
    for i in range(4):
        for j in range(4):
            transformation[i, j] = matrix.GetElement(i, j)
    return transformation


def validate_vtk_matrix_4x4(matrix):
    """
    Checks that a matrix is a vtkMatrix4x4.
    :param matrix: vtkMatrix4x4
    :raises TypeError
    :return: True
    """
    if not isinstance(matrix, vtk.vtkMatrix4x4):
        raise TypeError('Invalid matrix object passed')


def create_matrix_from_list(params, is_in_radians=False):
    """
    Generates a 4x4 numpy ndarray from a list of
    rx,ry,rz,tx,ty,tz in degrees, millimetres.

    This is designed to match VTK. VTK states that vtkProp3D uses
    'Orientation is specified as X,Y and Z rotations in that order,
    but they are performed as RotateZ, RotateX, and finally RotateY. However
    vtkTransform by default uses pre-multiplication. So, in mathematical
    notation, this would be written as

    [Output Point] = [RotateZ][RotateX][RotateY][Input Point]

    which, if you read the maths expression from right to left, would
    actually be termed RotateY, then RotateX, then RotateZ.

    The function in scikit-surgerycore called construct_rotm_from_euler
    takes an input string, e.g. 'zxy' and follows mathematical notation.
    So, 'zxy' means RotateY, RotateX, RotateZ in that order, reading
    from right to left, and so matches VTK.

    Furthermore, the construct_rotm_from_euler function in scikit-surgerycore
    expectes the user to pass the parameters in, in the order specified
    in the provided string.

    :param params list of exactly 6 numbers.
    :param is_in_radians: True if radians, False otherwise, default is False
    """
    if len(params) != 6:
        raise ValueError("Incorrect list size:" + str(params))

    rot = tm.construct_rotm_from_euler(params[2],
                                       params[0],
                                       params[1],
                                       sequence='zxy',
                                       is_in_radians=is_in_radians
                                       )
    trans = np.ndarray((3, 1))
    trans[0] = params[3]
    trans[1] = params[4]
    trans[2] = params[5]
    mat = tm.construct_rigid_transformation(rot, trans)
    return mat


def create_matrix_from_string(parameter_string, is_in_radians=False):
    """
    Generates a 4x4 numpy ndarray from a comma separated
    string of the format rx,ry,rz,tx,ty,tz in degrees, millimetres.

    :param parameter_string: rx,ry,rz,tx,ty,tz in degrees/millimetres
    :param is_in_radians: True if radians, False otherwise, default is False
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

    return create_matrix_from_list(param_list, is_in_radians)


def calculate_l2r_matrix(left_extrinsics: np.ndarray,
                         right_extrinsics: np.ndarray) -> np.ndarray:
    """
    Return the left to right transformation matrix:
        l2r = R * L^-1
    """
    l2r = np.matmul(right_extrinsics, np.linalg.inv(left_extrinsics))
    return l2r


def get_l2r_smartliver_format(l2r_matrix: np.ndarray) -> np.ndarray:
    """
    Convert 4x4 left to right matrix to smartliver l2r format:

    R1 R2 R3
    R4 R5 R6
    R7 R8 R9
    T1 T2 T3
    """
    rot = l2r_matrix[:3, :3]
    translation = l2r_matrix[:3, 3]

    l2r_smartliver_format = np.vstack((rot, translation))

    return l2r_smartliver_format
