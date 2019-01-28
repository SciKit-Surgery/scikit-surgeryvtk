# -*- coding: utf-8 -*-

import pytest
import numpy as np
import six

import sksurgeryvtk.utils.projection_utils as pu


def test_project_points_invalid_as_input_null():

    with pytest.raises(ValueError):
        pu.project_points(None, None, None, None)

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), None, None, None)

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), np.zeros([4, 4]), None, None)


def test_project_points_invalid_as_points_not_numpy_array():

    with pytest.raises(TypeError):
        pu.project_points("invalid", np.zeros([4, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_points_not_2d_matrix():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3, 4]), np.zeros([4, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_points_not_3_columns():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 4]), np.zeros([4, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_not_numpy_array():

    with pytest.raises(TypeError):
        pu.project_points(np.zeros([4, 3]), "invalid", np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_not_2d():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), np.zeros([4, 4, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_wrong_number_rows():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), np.zeros([5, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_wrong_number_columns():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), np.zeros([4, 5]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_intrinsics_wrong_size():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), np.zeros([4, 4]), np.zeros([2, 2]), np.zeros([1, 4]))


def test_project_points_invalid_as_distortion_wrong_number_rows():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 3]), np.zeros([4, 4]), np.zeros([3, 3]), np.zeros([2, 4]))


def test_project_facing_points_invalid_as_normals_null():

    with pytest.raises(ValueError):
        pu.project_facing_points(np.zeros([4, 3]), None, np.zeros([4, 4]), np.zeros([3, 3]))


def test_project_facing_points_invalid_as_normals_not_numpy_array():

    with pytest.raises(TypeError):
        pu.project_facing_points(np.zeros([4, 3]), "hello", np.zeros([4, 4]), np.zeros([3, 3]))


def test_project_facing_points_invalid_as_normals_shape_doesnt_match_points():

    with pytest.raises(ValueError):
        pu.project_facing_points(np.zeros([4, 3]), np.zeros([4, 4]), np.zeros([4, 4]), np.zeros([3, 3]))


def test_project_facing_points_valid_example_synthetic_data():

    points = np.zeros([3, 3])
    normals = np.zeros([3, 3])
    world_to_camera = np.eye(4)

    # Not a valid projection matrix, so don't
    # expect any sensible pixel locations.
    camera_matrix = np.eye(3)

    # Camera at origin, points along z-axis
    points[0][2] = 10
    points[1][2] = 11
    points[2][2] = 12

    # Normals pick 3 directions
    normals[0][2] = -1  # facing back to camera
    normals[1][0] = 1   # along x axis
    normals[2][1] = 1   # along y axis

    projected_points, facing_points = pu.project_facing_points(points,
                                                               normals,
                                                               world_to_camera,
                                                               camera_matrix)
    assert projected_points.shape[0] == 1
    assert facing_points.shape[0] == 1
    assert facing_points[0][0] == 0
    assert facing_points[0][1] == 0
    assert facing_points[0][2] == 10
