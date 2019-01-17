# -*- coding: utf-8 -*-

"""
Functions to setup a VTK camera to match the OpenCV calibrated camera.
"""

import vtk
import numpy as np

# pylint: disable=no-member


def create_vtk_matrix_from_numpy(array):
    """ Return a new vtkMatrix4x4 from a numpy array. """

    if not isinstance(array, np.ndarray):
        raise TypeError('Invalid array object passed')

    if array.shape != (4, 4):
        raise ValueError('Input array should be a 4x4 matrix')

    vtk_matrix = vtk.vtkMatrix4x4()
    vtk_matrix.DeepCopy(array.ravel())

    return vtk_matrix


def compute_projection_matrix(width,
                              height,
                              f_x,
                              f_y,
                              c_x,
                              c_y,
                              near,
                              far,
                              aspect_ratio):
    """
    Computes the OpenGL projection matrix.

    Inspired by:
    http://strawlab.org/2011/11/05/augmented-reality-with-OpenGL/

    which was also implemented in NifTK.

    :param width: window width in pixels
    :param height: window height in pixels
    :param f_x: focal length in x direction, (K_00)
    :param f_y: focal length in y direction, (K_11)
    :param c_x: principal point x coordinate, (K02)
    :param c_y: principal point y coordinate, (K12)
    :param near: near clipping distance in world coordinate frame units (mm).
    :param far:  far clipping distance in world coordinate frame units (mm).
    :param aspect_ratio: relative physical size of pixels, as x/y.
    :return: vtkMatrix4x4
    """

    matrix = vtk.vtkMatrix4x4()
    matrix.Zero()
    matrix.SetElement(0, 0, 2*f_x/width)
    matrix.SetElement(0, 1, -2*0/width)  # Not doing skew, so this will be 0.
    matrix.SetElement(0, 2, (width - 2*c_x)/width)
    matrix.SetElement(1, 1, 2*(f_y / aspect_ratio) / (height / aspect_ratio))
    matrix.SetElement(1, 2, (-(height / aspect_ratio)
                             + 2*(c_y/aspect_ratio))/(height / aspect_ratio))
    matrix.SetElement(2, 2, (-far-near)/(far-near))
    matrix.SetElement(2, 3, -2*far*near/(far-near))
    matrix.SetElement(3, 2, -1)
    return matrix


def set_camera_pose(vtk_camera, vtk_matrix):
    """
    Sets the camera position and orientation from a camera to world matrix.

    :param vtk_camera: a vtkCamera
    :param vtk_matrix: a vtkMatrix4x4 representing the camera to world.
    :return:
    """
    if not isinstance(vtk_camera, vtk.vtkCamera):
        raise TypeError('Invalid camera object passed')

    if not isinstance(vtk_matrix, vtk.vtkMatrix4x4):
        raise TypeError('Invalid matrix object passed')

    # This implies a right handed coordinate system.
    # By default, assume camera position is at origin,
    # looking down the world +ve z-axis.
    origin = [0, 0, 0, 1]
    focal_point = [0, 0, 1000, 1]
    view_up = [0, -1000, 0, 1]

    vtk_matrix.MultiplyPoint(origin, origin)
    vtk_matrix.MultiplyPoint(focal_point, focal_point)
    vtk_matrix.MultiplyPoint(view_up, view_up)
    view_up[0] = view_up[0] - origin[0]
    view_up[1] = view_up[1] - origin[1]
    view_up[2] = view_up[2] - origin[2]

    # We then move the camera to that position.
    vtk_camera.SetPosition(origin[0], origin[1], origin[2])
    vtk_camera.SetFocalPoint(focal_point[0], focal_point[1], focal_point[2])
    vtk_camera.SetViewUp(view_up[0], view_up[1], view_up[2])


def set_projection_matrix(vtk_camera, vtk_matrix):
    """
    Enable and Set the ProjectionTransformMatrix for a vtk camera.
    As a side effect, this sets UseExplicitProjectionTransformMatrixOn().
    """

    if not isinstance(vtk_camera, vtk.vtkCamera):
        raise TypeError('Invalid camera object passed')

    if not isinstance(vtk_matrix, vtk.vtkMatrix4x4):
        raise TypeError('Invalid matrix object passed')

    vtk_camera.UseExplicitProjectionTransformMatrixOn()
    vtk_camera.SetExplicitProjectionTransformMatrix(vtk_matrix)
