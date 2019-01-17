# -*- coding: utf-8 -*-

import csv
import pytest
import vtk
import numpy as np

import sksurgeryvtk.camera.vtk_camera_model as cam


def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_type():

    with pytest.raises(TypeError):
        cam.create_vtk_matrix_from_numpy("hello")


def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_shape():

    array = np .ones([2, 3])

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


def test_camera_projection():
    # See data:
    # chessboard_14_10_3.txt - 3D chessboard coordinates
    # left-1095.png - image taken of chessboard
    # left-1095.png.points.txt - detected 2D image points
    # calib.intrinsic.txt - top 3x3 matrix are intrinsic parameters
    # left-1095.extrinsic.txt - model to camera matrix, a.k.a camera extrinsics, a.k.a pose

    # Load 3D points, first column is the point identifier, then x,y,z
    number_model_points = 0
    model_points = []
    with open('tests/data/chessboard_14_10_3.txt', 'r') as model_points_file:
        model_reader = csv.reader(model_points_file, delimiter='\t')

        for row in model_reader:
            if len(row) != 4:
                raise ValueError('Line '
                                 + str(number_model_points)
                                 + ' does not contain '
                                 + 'ID and 3 numbers')
            model_points.append(row)
            number_model_points += 1

    # Load 2D points, first column is the point identifier, then x,y
    number_image_points = 0
    image_points = []
    with open('tests/data/left-1095.png.points.txt', 'r') as image_points_file:
        image_reader = csv.reader(image_points_file, delimiter=' ')

        for row in image_reader:
            if len(row) != 3:
                raise ValueError('Line '
                                 + str(number_image_points)
                                 + ' does not contain '
                                 + 'ID and 2 numbers')
            image_points.append(row)
            number_image_points += 1

    # Load intrinsics for projection matrix.
    intrinsics = []
    with open('tests/data/calib.intrinsic.txt', 'r') as intrinsics_file:
        intrinsics_reader = csv.reader(intrinsics_file, delimiter=' ')

        for row in intrinsics_reader:
            if len(row) != 3:
                raise ValueError('Invalid row in intrinsics matrix.')

            intrinsics.append(row)
            if len(intrinsics) == 3:
                break

    # Load extrinsics for camera pose (position, orientation).
    model_to_camera = vtk.vtkMatrix4x4()
    counter = 0
    with open('tests/data/left-1095.extrinsic.txt', 'r') as extrinsics_file:
        extrinsics_reader = csv.reader(extrinsics_file, delimiter=' ')

        for row in extrinsics_reader:
            if len(row) != 4:
                raise ValueError('Invalid row in extrinsics matrix.')

            model_to_camera.SetElement(counter, 0, float(row[0]))
            model_to_camera.SetElement(counter, 1, float(row[1]))
            model_to_camera.SetElement(counter, 2, float(row[2]))
            model_to_camera.SetElement(counter, 3, float(row[3]))
            counter += 1

    # OpenCV maps from chessboard to camera.
    # Assume chessboard == world, so the input matrix is world_to_camera.
    # We need camera_to_world to position the camera in world coordinates.
    # So, invert it.
    model_to_camera.Invert()

    assert number_model_points == 140
    assert number_image_points == 140
    assert len(image_points) == 140
    assert len(model_points) == 140

    projection_matrix = cam.compute_projection_matrix(1920, 1080,
                                                      float(intrinsics[0][0]), float(intrinsics[1][1]),
                                                      float(intrinsics[0][2]), float(intrinsics[1][2]),
                                                      0.01, 1000,
                                                      1
                                                      )
    vtk_camera = vtk.vtkCamera()
    cam.set_camera_pose(vtk_camera, model_to_camera)
    cam.set_projection_matrix(vtk_camera, projection_matrix)

    # Iterate through each point:
    # Project 3D to 2D pixel coordinates.
    # Measure RMS error.
    # Should be < 1pix RMS if we had an undistorted image, and 2D points detected
    # from those undistorted images. However, the test data is normally
    # the original image from the camera, and includes distortion, and the
    # corner locations therefore are distorted as well.
    # So, lets just assume that the error should be < 10pix RMS.
    # This assumes: If any of the camera calibration maths is wrong, or you have
    # matrices in the wrong order, or you are flipped or inverted, you get
    # much bigger errors than this.

    allowable_error = 10.0
