# -*- coding: utf-8 -*-

import numpy as np
import pytest

import sksurgeryvtk.models.vtk_point_model as pm


def test_point_model_invalid_because_null_points():
    with pytest.raises(ValueError):
        pm.VTKPointModel(None, None)


def test_point_model_invalid_because_null_colours():
    with pytest.raises(ValueError):
        pm.VTKPointModel(np.ones((1, 3)), None)


def test_point_model_invalid_because_points_not_numpy_array():
    with pytest.raises(TypeError):
        pm.VTKPointModel(1, np.ones((1, 3)))


def test_point_model_invalid_because_colours_not_numpy_array():
    with pytest.raises(TypeError):
        pm.VTKPointModel(np.ones((1, 3)), 1)


def test_point_model_invalid_because_points_not_got_3_columns():
    with pytest.raises(ValueError):
        pm.VTKPointModel(np.ones((1, 2)), np.ones((1, 3)))


def test_point_model_invalid_because_colours_not_got_3_columns():
    with pytest.raises(ValueError):
        pm.VTKPointModel(np.ones((1, 3)), np.ones((1, 2)))


def test_point_model_invalid_because_no_points():
    with pytest.raises(ValueError):
        pm.VTKPointModel(np.ones((0, 3)), np.ones((1, 3)))


def test_point_model_invalid_because_no_colours():
    with pytest.raises(ValueError):
        pm.VTKPointModel(np.ones((1, 3)), np.ones((0, 3)))


def test_point_model_invalid_because_different_shape():
    with pytest.raises(ValueError):
        pm.VTKPointModel(np.ones((1, 3)), np.ones((2, 3)))


def test_point_model_invalid_because_points_not_float():
    with pytest.raises(TypeError):
        pm.VTKPointModel(np.ones((1, 3), dtype=int),
                         np.ones((1, 3), dtype=int))


def test_point_model_invalid_because_colours_not_uchar():
    with pytest.raises(TypeError):
        pm.VTKPointModel(np.ones((1, 3), dtype=float),
                         np.ones((1, 3), dtype=int))


def test_point_model_invalid_because_opacity_not_float():
    with pytest.raises(TypeError):
        pm.VTKPointModel(np.ones((1, 6)), 1)


def test_point_model_invalid_because_opacity_too_low():
    with pytest.raises(TypeError):
        pm.VTKPointModel(np.ones((1, 6)), -0.1)


def test_point_model_invalid_because_opacity_too_high():
    with pytest.raises(TypeError):
        pm.VTKPointModel(np.ones((1, 6)), -1.1)


def test_points_model_4_points():
    points = np.zeros((4, 3), dtype=float)
    points[1][0] = 1
    points[2][1] = 1
    points[3][2] = 1
    colours = np.zeros((4, 3), dtype=np.uint8)
    colours[1][0] = 255
    colours[2][1] = 255
    colours[3][2] = 255

    vtk_model = pm.VTKPointModel(points, colours)
    assert vtk_model.get_point_size() == 5
    assert vtk_model.get_number_of_points() == 4
