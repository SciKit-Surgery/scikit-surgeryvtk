# -*- coding: utf-8 -*-

"""
Tests for the vtk cylinder source.
"""

import pytest

import sksurgeryvtk.models.vtk_cylinder_model as cm


def test_cylinder_model_invalid():
    """
    Tests what happens when we pass rubbish, type error
    should be passed back from vtkCyclinderSource
    """
    with pytest.raises(TypeError):
        cm.VTKCylinderModel(None, 0.5)


def test_cylinder_model(setup_vtk_overlay_window):
    """
    Tests that a widget can access the actor created.

    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    height = 50.0
    radius = 10.0
    colour = (0.0, 1.0, 0.0)
    name = "test Cylinder"
    angle = 45.0
    orientation = (1.0, 0.0, 0.0)
    resolution = 45
    visibility = True
    opacity = 0.5

    vtk_model = cm.VTKCylinderModel(height, radius, colour, name, angle,
                                    orientation, resolution, visibility,
                                    opacity)

    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window
    widget.add_vtk_actor(vtk_model.actor)
    widget.AddObserver("ExitEvent", lambda o, e, a=_pyside_qt_app: a.quit())

    widget.show()
    widget.Initialize()
    widget.Start()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    #_pyside_qt_app.exec()
    widget.close()

