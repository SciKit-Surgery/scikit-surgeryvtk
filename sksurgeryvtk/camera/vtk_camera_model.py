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


def compute_right_camera_pose(left_camera_to_world, left_to_right):
    """
    Returns the right_camera_to_world, computed from the combination
    of left_camera_to_world, and left_to_right.

    :param left_camera_to_world: 4x4 numpy ndarray representing rigid transform
    :param left_to_right: 4x4 numpy ndarray representing rigid transform
    :return: right_camera_to_world
    """
    left_world_to_camera = np.linalg.inv(left_camera_to_world)
    right_world_to_camera = np.matmul(left_to_right, left_world_to_camera)
    right_camera_to_world = np.linalg.inv(right_world_to_camera)
    return right_camera_to_world


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

    which was also implemented in NifTK:
    https://cmiclab.cs.ucl.ac.uk/CMIC/NifTK/blob/master/MITK/Modules/Core/Rendering/vtkOpenGLMatrixDrivenCamera.cxx#L119

    :param width: image width in pixels
    :param height: image height in pixels
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


def compute_scissor(window_width,
                    window_height,
                    image_width,
                    image_height,
                    aspect_ratio):
    """
    Used on vtkCamera when you are trying to set the viewport to only render
    to a part of the total window size. For example, this occurs when you
    have calibrated a video camera using OpenCV, on images of 1920 x 1080,
    and then you are displaying in a VTK window that is twice as wide/high.

    This was inplemented in NifTK:
    https://cmiclab.cs.ucl.ac.uk/CMIC/NifTK/blob/master/MITK/Modules/Core/Rendering/vtkOpenGLMatrixDrivenCamera.cxx#L129

    but it appears it should be available in VTK now:
    https://gitlab.kitware.com/vtk/vtk/merge_requests/882

    :param window_width: in pixels
    :param window_height: in pixels
    :param image_width: in pixels
    :param image_height: in pixels
    :param aspect_ratio: relative physical size of pixels, as x/y.
    :return: scissor_x, scissor_y, scissor_width, scissor_height in pixels
    """
    width_scale = window_width / image_width
    height_scale = window_height / image_height / aspect_ratio

    vpw = window_width
    vph = window_height

    if width_scale < height_scale:
        vph = int((image_height / aspect_ratio) * width_scale)
    else:
        vpw = int(image_width * height_scale)

    vpx = int((window_width / 2.0) - (vpw / 2.0))
    vpy = int((window_height / 2.0) - (vph / 2.0))

    return vpx, vpy, vpw, vph


def compute_viewport(window_width,
                     window_height,
                     scissor_x,
                     scissor_y,
                     scissor_width,
                     scissor_height):
    """
    Computes the VTK viewport dimensions which range [0-1] in x and y.

    :param window_width: in pixels
    :param window_height: in pixels
    :param scissor_x: output from compute_scissor
    :param scissor_y: output from compute_scissor
    :param scissor_width: output from compute_scissor
    :param scissor_height: output from compute_scissor
    :return:
    """
    x_min = scissor_x / window_width
    y_min = scissor_y / window_height
    x_max = scissor_width / window_width + x_min
    y_max = scissor_height / window_height + y_min
    return x_min, y_min, x_max, y_max


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
