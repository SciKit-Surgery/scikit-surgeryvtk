# -*- coding: utf-8 -*-

import platform
from sksurgeryvtk.models.vtk_image_model import VTKImageModel


def test_valid_vtk_image_actor():
    input_file = 'tests/data/calibration/left-1095-undistorted.png'
    model = VTKImageModel(input_file)

    assert model.actor is not None


def test_image_model_overlay(vtk_overlay_with_gradient_image):
    """

    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    image, widget, _, _pyside_qt_app = vtk_overlay_with_gradient_image
    input_file = 'tests/data/calibration/left-1095-undistorted.png'
    model = [VTKImageModel(input_file)]
    widget.add_vtk_models(model)
    widget.resize(1920, 1080)
    widget.Render()
    widget.show()  # Startup the widget
    if 'Linux' in platform.system():
        widget.Initialize()  # Allows the interactor to initialize itself.
        widget.Start()  # Start the event loop.
    else:
        print("\nYou've elected to initialize the VTKOverlayWindow(),",
              "be sure to do it in your calling function.")

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    widget.close()
