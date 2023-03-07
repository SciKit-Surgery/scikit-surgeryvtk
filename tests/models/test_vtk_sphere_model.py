# -*- coding: utf-8 -*-

import numpy as np
import pytest

import sksurgeryvtk.models.vtk_sphere_model as sm


def test_sphere_model_invalid_because_null_points():
    with pytest.raises(ValueError):
        sm.VTKSphereModel(None, 0.5)


def test_sphere_model_invalid_because_points_not_numpy_array():
    with pytest.raises(TypeError):
        sm.VTKSphereModel(1, 0.5)


def test_sphere_model_invalid_because_points_not_got_3_columns():
    with pytest.raises(ValueError):
        sm.VTKSphereModel(np.ones((1, 2)), 0.5)


def test_sphere_model_invalid_because_no_points():
    with pytest.raises(ValueError):
        sm.VTKSphereModel(np.ones((0, 3)), 0.5)


def test_sphere_model_invalid_because_points_not_float():
    with pytest.raises(TypeError):
        sm.VTKSphereModel(np.ones((1, 3), dtype=int), 0.5)


def test_sphere_model_invalid_because_radius_not_positive():
    with pytest.raises(ValueError):
        sm.VTKSphereModel(np.eye(3), -1)


def test_sphere_model_3_points(setup_vtk_overlay_window):
    points = np.eye(3, dtype=float)
    vtk_model = sm.VTKSphereModel(points, 0.5)

    widget, _, app = setup_vtk_overlay_window
    widget.add_vtk_actor(vtk_model.actor)
    widget.show()
    # app.exec_()
