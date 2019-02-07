# -*- coding: utf-8 -*-

import pytest
from sksurgeryvtk.models.vtk_image_model import VTKImageModel


def test_valid_image_model_matt():
    input_file = 'tests/data/calibration/left-1095-undistorted.png'
    model = VTKImageModel(input_file)
    assert model.actor is not None


def test_image_model_overlay(vtk_overlay_with_gradient_image):

    image, widget, _, _, app = vtk_overlay_with_gradient_image
    input_file = 'tests/data/calibration/left-1095-undistorted.png'
    model = [VTKImageModel(input_file)]
    widget.add_vtk_models(model)
    widget.resize(1920, 1080)
    widget.show()
    widget.Render()
    #app.exec_()

