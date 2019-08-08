# -*- coding: utf-8 -*-

"""
Tests for the vtk cylinder source.
"""

import pytest
import sksurgeryvtk.widgets.vtk_overlay_window as ow
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

    widget, _, _, _ = setup_vtk_overlay_window

    widget = ow.VTKOverlayWindow()
    widget.add_vtk_actor(vtk_model.actor)
    widget.show()
