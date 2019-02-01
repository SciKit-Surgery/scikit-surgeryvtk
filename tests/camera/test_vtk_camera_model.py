# -*- coding: utf-8 -*-

import pytest
import vtk
import six
import cv2
import numpy as np
import sksurgeryvtk.camera.vtk_camera_model as cam
from PySide2.QtCore import QRect

def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_type():

    with pytest.raises(TypeError):
        cam.create_vtk_matrix_from_numpy("hello")


def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_shape():

    array = np.ones([2, 3])

    with pytest.raises(ValueError):
        cam.create_vtk_matrix_from_numpy(array)


def test_create_vtk_matrix_4x4_from_numpy():

    array = np.random.rand(4, 4)

    vtk_matrix = cam.create_vtk_matrix_from_numpy(array)

    for i in range(4):
        for j in range(4):
            assert vtk_matrix.GetElement(i, j) == array[i, j]


def test_set_projection_matrix_fail_on_invalid_camera():

    not_a_camera = np.ones([5, 5])
    vtk_matrix = vtk.vtkMatrix4x4()

    with pytest.raises(TypeError):
        cam.set_projection_matrix(not_a_camera,  vtk_matrix)


def test_set_projection_matrix_fail_on_invalid_matrix():

    camera = vtk.vtkCamera()
    not_a_vtk_matrix = np.ones([5, 5])

    with pytest.raises(TypeError):
        cam.set_projection_matrix(camera,  not_a_vtk_matrix)


def test_compute_projection_matrix_from_intrinsics():

    matrix = cam.compute_projection_matrix(1920, 1080,                # w, y
                                           2012.186314, 2017.966019,  # fx, fy,
                                           944.7173708, 617.1093984,  # cx, cy,
                                           0.1, 1000,                 # near, far
                                           1                          # aspect ratio
                                           )
    camera = vtk.vtkCamera()

    cam.set_projection_matrix(camera, matrix)

    output = camera.GetExplicitProjectionTransformMatrix()
    assert matrix == output


def test_set_pose_identity_should_give_origin():

    np_matrix = np.eye(4)
    vtk_matrix = cam.create_vtk_matrix_from_numpy(np_matrix)

    vtk_camera = vtk.vtkCamera()
    cam.set_camera_pose(vtk_camera, vtk_matrix)

    position = vtk_camera.GetPosition()
    focal_point = vtk_camera.GetFocalPoint()
    view_up = vtk_camera.GetViewUp()

    # Identity matrix should give:
    # Position at origin
    # Facing along positive z axis
    # If x points right in the image, y axis points down.
    assert position == (0, 0, 0)
    assert focal_point[2] > 0
    assert view_up == (0, -1, 0)


def test_camera_projection(setup_vtk_overlay_window):

    vtk_overlay, factory, vtk_std_err, setup_qt = setup_vtk_overlay_window

    # See data:
    # chessboard_14_10_3_no_ID.txt - 3D chessboard coordinates
    # left-1095.png - image taken of chessboard
    # left-1095.png.points.txt - detected 2D image points
    # calib.intrinsic.txt - top 3x3 matrix are intrinsic parameters
    # left-1095.extrinsic.txt - model to camera matrix, a.k.a camera extrinsics, a.k.a pose

    # Load 3D points
    model_points_file = 'tests/data/calibration/chessboard_14_10_3_no_ID.txt'
    model_points = np.loadtxt(model_points_file)
    number_model_points = model_points.shape[0]

    # Load images
    left_image = cv2.imread('tests/data/calibration/left-1095-undistorted.png')

    # Load 2D points
    image_points_file ='tests/data/calibration/left-1095-undistorted.png.points.txt'
    image_points = np.loadtxt(image_points_file)
    number_image_points = image_points.shape[0]

    # Load intrinsics for projection matrix.
    intrinsics_file = 'tests/data/calibration/calib.left.intrinsic.txt'
    intrinsics = np.loadtxt(intrinsics_file)

    # Load extrinsics for camera pose (position, orientation).
    extrinsics_file = 'tests/data/calibration/left-1095.extrinsic.txt'
    extrinsics = np.loadtxt(extrinsics_file)

    # OpenCV maps from chessboard to camera.
    # Assume chessboard == world, so the input matrix is world_to_camera.
    # We need camera_to_world to position the camera in world coordinates.
    # So, invert it.
    camera_to_world = np.linalg.inv(extrinsics)

    assert number_model_points == 140
    assert number_image_points == 140
    assert len(image_points) == 140
    assert len(model_points) == 140

    screen = setup_qt.primaryScreen()
    width = left_image.shape[1]
    height = left_image.shape[0]
    while width >= screen.geometry().width() or height >= screen.geometry().height():
        width //= 2
        height //= 2

    vtk_scale_x = left_image.shape[1] / width
    vtk_scale_y = left_image.shape[0] / height

    vtk_overlay.set_video_image(left_image)
    vtk_overlay.set_camera_pose(camera_to_world)
    vtk_overlay.set_camera_matrix(intrinsics)
    vtk_overlay.resize(width, height)
    vtk_overlay.show()

    renderer = vtk_overlay.get_foreground_renderer()

    six.print_('Left image = (' + str(left_image.shape[1]) + ', ' + str(left_image.shape[0]) + ')')
    six.print_('Chosen size = (' + str(width) + ', ' + str(height) + ')')
    six.print_('Render window = ' + str(vtk_overlay.GetRenderWindow().GetSize()))
    six.print_('Widget = (' + str(vtk_overlay.width()) + ', ' + str(vtk_overlay.height()) + ')')
    six.print_('Viewport = ' + str(renderer.GetViewport()))

    # Project points using OpenCV.
    projected_points = vtk_overlay.project_points(model_points)

    # Iterate through each point:
    # Project 3D to 2D pixel coordinates.
    # Measure RMS error.
    # Should be about 1pix RMS if we had an undistorted image,
    # and 2D points detected from those undistorted images.
    # This assumes: If any of the camera calibration maths is wrong, or you have
    # matrices in the wrong order, or you are flipped or inverted, you get
    # much bigger errors than this.

    coord_3d = vtk.vtkCoordinate()
    coord_3d.SetCoordinateSystemToWorld()
    counter = 0
    rms_vtk = 0
    rms_opencv = 0

    for m_c in model_points:

        coord_3d.SetValue(float(m_c[0]), float(m_c[1]), float(m_c[2]))
        i_c = image_points[counter]

        # This will scale to the window, which may well be a different size to the original image.
        p_x, p_y = coord_3d.GetComputedDoubleDisplayValue(renderer)

        # Scale them up to the right image size.
        p_x *= vtk_scale_x
        p_y *= vtk_scale_y

        # And flip the y-coordinate, as OpenGL numbers Y from bottom up, OpenCV numbers top-down.
        p_y = left_image.shape[0] - 1 - p_y  #

        # Difference between VTK points and reference points.
        dx = p_x - float(i_c[0])
        dy = p_y - float(i_c[1])
        rms_vtk += (dx * dx + dy * dy)

        # Difference between OpenCV projectPoints and reference points.
        dx = projected_points[counter][0][0] - float(i_c[0])
        dy = projected_points[counter][0][1] - float(i_c[1])
        rms_opencv += (dx * dx + dy * dy)

        counter += 1

    rms_vtk /= float(counter)
    rms_vtk = np.sqrt(rms_vtk)

    rms_opencv /= float(counter)
    rms_opencv = np.sqrt(rms_opencv)

    six.print_('rms_vtk=' + str(rms_vtk) + ', rms_opencv=' + str(rms_opencv))

    assert rms_vtk < 1.51
    assert rms_opencv < 0.7



