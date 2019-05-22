# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import pytest
import vtk
import six
import numpy as np
import sksurgeryvtk.widgets.vtk_overlay_window as ow
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
        sm.VTKSphereModel(np.ones((1, 3), dtype=np.int), 0.5)


def test_sphere_model_invalid_because_radius_not_positive():
    with pytest.raises(ValueError):
        sm.VTKSphereModel(np.eye(3), -1)


def test_sphere_model_3_points(setup_vtk_overlay_window):
    points = np.eye(3, dtype=np.float)
    vtk_model = sm.VTKSphereModel(points, 0.5)

    widget, _, _, app = setup_vtk_overlay_window

    widget = ow.VTKOverlayWindow()
    widget.add_vtk_actor(vtk_model.actor)
    widget.show()
    #app.exec_()
