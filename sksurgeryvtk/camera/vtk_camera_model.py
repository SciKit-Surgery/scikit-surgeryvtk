# -*- coding: utf-8 -*-

"""
Functions to setup a VTK camera to match the OpenCV calibrated camera.
"""

import vtk
import numpy as np


def compute_right_camera_pose(left_camera_to_world, left_to_right):
    """
    Returns the right_camera_to_world, computed from the combination
    of left_camera_to_world, and left_to_right.

    :param left_camera_to_world: 4x4 numpy ndarray representing rigid transform
    :param left_to_right: 4x4 numpy ndarray representing rigid transform
    :return: right_camera_to_world as 4x4 numpy ndarray
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
    # pylint: disable=line-too-long
    """
    Computes the OpenGL projection matrix.

    Thanks to:
    `Andrew Straw <http://strawlab.org/2011/11/05/augmented-reality-with-OpenGL/>`_.

    whose method was also implemented in:
    `NifTK <https://cmiclab.cs.ucl.ac.uk/CMIC/NifTK/blob/master/MITK/Modules/Core/Rendering/vtkOpenGLMatrixDrivenCamera.cxx#L119>`_.

    Note: If you use this method, the display will look ok, but as of VTK 8.1.0,
    it won't work with vtkWindowToImageFilter, as the window to image filter
    tries to render the image in tiles. This requires instantiating temporary
    new vtkCamera, and the vtkCamera copy constructor, shallow copy and deep copy
    do not actually copy the UseExplicitProjectionTransformMatrixOn or
    ExplicitProjectionTransformMatrix.

    :param width: image width in pixels
    :param height: image height in pixels
    :param f_x: focal length in x direction, (K_00)
    :param f_y: focal length in y direction, (K_11)
    :param c_x: principal point x coordinate, (K_02)
    :param c_y: principal point y coordinate, (K_12)
    :param near: near clipping distance in world coordinate frame units (mm)
    :param far:  far clipping distance in world coordinate frame units (mm)
    :param aspect_ratio: relative physical size of pixels, as x/y
    :return: vtkMatrix4x4 containing a 4x4 projection matrix
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
    # pylint: disable=line-too-long
    """
    Used on vtkCamera when you are trying to set the viewport to only render
    to a part of the total window size. For example, this occurs when you
    have calibrated a video camera using OpenCV, on images of 1920 x 1080,
    and then you are displaying in a VTK window that is twice as wide/high.

    This was implemented in:
    `NifTK <https://cmiclab.cs.ucl.ac.uk/CMIC/NifTK/blob/master/MITK/Modules/Core/Rendering/vtkOpenGLMatrixDrivenCamera.cxx#L129>`_.

    and it appears it should also be available in:
    `VTK <https://gitlab.kitware.com/vtk/vtk/merge_requests/882>`_.

    :param window_width: in pixels
    :param window_height: in pixels
    :param image_width: in pixels
    :param image_height: in pixels
    :param aspect_ratio: relative physical size of pixels, as x/y.
    :return: scissor_x, scissor_y, scissor_width, scissor_height in pixels
    """
    width_scale = window_width / image_width
    height_scale = window_height / (image_height / aspect_ratio)

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
    Used on vtkCamera when you are trying to set the viewport to only render
    to a part of the total window size. For example, this occurs when you
    have calibrated a video camera using OpenCV, on images of 1920 x 1080,
    and then you are displaying in a VTK window that is twice as wide/high.

    :param window_width: in pixels
    :param window_height: in pixels
    :param scissor_x: output from compute_scissor
    :param scissor_y: output from compute_scissor
    :param scissor_width: output from compute_scissor
    :param scissor_height: output from compute_scissor
    :return: x_min, y_min, x_max, y_max as normalised viewport coordinates
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

    Warning: This won't work with vtkWindowToImageFilter.
    """
    if not isinstance(vtk_camera, vtk.vtkCamera):
        raise TypeError('Invalid camera object passed')

    if not isinstance(vtk_matrix, vtk.vtkMatrix4x4):
        raise TypeError('Invalid matrix object passed')

    vtk_camera.UseExplicitProjectionTransformMatrixOn()
    vtk_camera.SetExplicitProjectionTransformMatrix(vtk_matrix)


def set_camera_intrinsics(vtk_camera,
                          width,
                          height,
                          f_x,
                          f_y,
                          c_x,
                          c_y,
                          near,
                          far
                         ):
    # pylint: disable=line-too-long
    """
    Used to setup a vtkCamera according to OpenCV conventions.

    Thanks to: `benoitrosa <https://gist.github.com/benoitrosa/ffdb96eae376503dba5ee56f28fa0943>`_

    :param vtk_camera: vtkCamera
    :param width: image width in pixels
    :param height: image height in pixels
    :param f_x: focal length in x direction, (K_00)
    :param f_y: focal length in y direction, (K_11)
    :param c_x: principal point x coordinate, (K_02)
    :param c_y: principal point y coordinate, (K_12)
    :param near: near clipping distance in world coordinate frame units (mm).
    :param far:  far clipping distance in world coordinate frame units (mm).
    """
    vtk_camera.SetClippingRange(near, far)

    wcx = (-2.0 * (c_x - width / 2.0) / width)
    wcy = 2.0 * (c_y - height / 2.0) / height

    vtk_camera.SetWindowCenter(wcx, wcy)

    # Set vertical view angle as an indirect way of setting the y focal distance
    angle = 180 / np.pi * 2.0 * np.arctan2(height / 2.0, f_y)
    vtk_camera.SetViewAngle(angle)

    # If you see the above link to benoitrosa, then the benoitrosa method
    # just sets the aspect ratio, for scaling, as a way to set
    # the x focal distance.
    #
    # i.e. like this:
    #
    #    mat = np.eye(4)
    #    aspect = f_y / f_x
    #    mat[0, 0] = 1.0 / aspect
    #    trans = vtk.vtkTransform()
    #    trans.SetMatrix(mat.flatten())
    #    vtk_camera.SetUserTransform(trans)
    #
    # However it was found to incorrectly affect the
    # x window centre settings as well. So instead,
    # we do the following. Based on the following order of transformations:
    #
    # Actual Projection Matrix = UserTransform * Projection * Shear * View
    #
    # (reading right to left as usual).

    # So, first, set an identity UserTransform.
    vtk_user_mat = vtk.vtkMatrix4x4()
    vtk_user_mat.Identity()
    vtk_user_trans = vtk.vtkTransform()
    vtk_user_trans.SetMatrix(vtk_user_mat)
    vtk_camera.SetUserTransform(vtk_user_trans)

    # Retrieve the current projection matrix, which includes UserTransform.
    # That's why we had to ensure it was the identity just above.
    vtk_proj = vtk_camera.GetProjectionTransformMatrix(1, -1, 1)

    # Calculate aspect ratio as per benoitrosa.
    aspect = f_y / f_x

    # Additionally calculate a shear to fix the window centre.
    shear = \
        (vtk_proj.GetElement(0, 2) \
         - (vtk_proj.GetElement(0, 2) * (1.0/aspect))) \
        / ((1.0/aspect) * vtk_proj.GetElement(0, 0))

    # Now set the aspect ratio as per benoitrosa.
    vtk_user_mat.SetElement(0, 0, 1.0/aspect)
    vtk_user_trans.SetMatrix(vtk_user_mat)
    vtk_camera.SetUserTransform(vtk_user_trans)

    # Additionally set the shear on the camera.
    vtk_camera.SetViewShear(shear, 0, 0)
