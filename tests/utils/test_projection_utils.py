# -*- coding: utf-8 -*-

import pytest
import numpy as np

import sksurgeryvtk.utils.projection_utils as pu


def test_project_points_invalid_as_input_null():

    with pytest.raises(ValueError):
        pu.project_points(None, None, None, None)

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), None, None, None)

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([4, 4]), None, None)


def test_project_points_invalid_as_points_not_numpy_array():

    with pytest.raises(TypeError):
        pu.project_points("invalid", np.zeros([4, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_not_numpy_array():

    with pytest.raises(TypeError):
        pu.project_points(np.zeros([4, 2]), "invalid", np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_not_2d():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([4, 4, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_wrong_number_rows():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([5, 4]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_extrinsics_wrong_number_columns():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([4, 5]), np.zeros([3, 3]), None)


def test_project_points_invalid_as_intrinsics_wrong_size():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([4, 4]), np.zeros([2, 2]), np.zeros([1, 4]))


def test_project_points_invalid_as_distortion_wrong_number_rows():

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([4, 4]), np.zeros([3, 3]), np.zeros([2, 4]))
