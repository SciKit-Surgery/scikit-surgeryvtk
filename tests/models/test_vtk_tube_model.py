# -*- coding: utf-8 -*-

import numpy as np
import pytest

import sksurgeryvtk.models.vtk_tube_model as tm


def test_tube_model_invalid_because_null_points():
    with pytest.raises(ValueError):
        tm.VTKTubeModel(None, [1.0, 1.0, 1.0])


def test_tube_model_invalid_because_points_not_numpy_array():
    with pytest.raises(TypeError):
        tm.VTKTubeModel(1, [1.0, 1.0, 1.0])


def test_sphere_model_invalid_because_points_not_got_3_columns():
    with pytest.raises(ValueError):
        tm.VTKTubeModel(np.ones((1, 2)), [1.0, 1.0, 1.0])


def test_sphere_model_invalid_because_no_points():
    with pytest.raises(ValueError):
        tm.VTKTubeModel(np.ones((0, 3)), [1.0, 1.0, 1.0])


def test_sphere_model_invalid_because_points_not_float():
    with pytest.raises(TypeError):
        tm.VTKTubeModel(np.ones((1, 3), dtype=int), [1.0, 1.0, 1.0])


def test_sphere_model_invalid_because_radius_not_positive():
    with pytest.raises(ValueError):
        tm.VTKTubeModel(np.eye(3), [1.0, 1.0, 1.0], radius=-1)


def test_sphere_model_invalid_because_number_of_sides_not_positive():
    with pytest.raises(ValueError):
        tm.VTKTubeModel(np.eye(3), [1.0, 1.0, 1.0], number_of_sides=-1)


def test_tube_model_3_points(setup_vtk_overlay_window):
    points = np.zeros((3, 3), dtype=float)
    points[1, 0] = 100.0
    points[2, 0] = 200.0
    vtk_model = tm.VTKTubeModel(points, [1.0, 0.0, 0.0], 40,20)
    widget, _, app = setup_vtk_overlay_window
    widget.add_vtk_actor(vtk_model.actor)
    widget.show()
    assert vtk_model.get_number_of_points() == 3
    assert vtk_model.get_radius() == 40
    assert vtk_model.get_number_of_sides() == 20
    vtk_model.set_radius(1)
    assert vtk_model.get_radius() == 1
    vtk_model.set_number_of_sides(4)
    assert vtk_model.get_number_of_sides() == 4
    assert vtk_model.get_colour()[0] == 1.0
    assert vtk_model.get_colour()[1] == 0.0
    assert vtk_model.get_colour()[2] == 0.0
    #app.exec_()