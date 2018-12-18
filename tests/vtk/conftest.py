# -*- coding: utf-8 -*-

import pytest
from PySide2.QtWidgets import QApplication
import numpy as np
import vtk
from sksurgeryoverlay.vtk.vtk_overlay_window import VTKOverlayWindow


@pytest.fixture(scope="session")
def setup_qt():
    """ Create the QT application. """
    app = QApplication([])
    return app


# Note: These windows will persist while all unit tests run.
#       Don't waste time trying to debug this.
@pytest.fixture(scope="module")
def vtk_overlay(setup_qt):
    """ Creates a VTKOverlayWindow with blank background image. """
    image = np.ones((150, 100, 3), dtype=np.uint8)
    factory = vtk.vtkGraphicsFactory()
    factory.SetOffScreenOnlyMode(1)
    factory.SetUseMesaClasses(1)
    vtk_overlay = VTKOverlayWindow()
    vtk_overlay.GetRenderWindow().SetOffScreenRendering(1)
    vtk_overlay.set_video_image(image)
    return vtk_overlay


# Note: These windows will persist while all unit tests run.
#       Don't waste time trying to debug this.
@pytest.fixture(scope="module")
def vtk_overlay_with_gradient_image(setup_qt):
    """ Creates a VTKOverlayWindow with gradient image. """
    width = 512
    height = 256
    image = np.ones((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            image[y][x][0] = y
            image[y][x][1] = y
            image[y][x][2] = y
    factory = vtk.vtkGraphicsFactory()
    factory.SetOffScreenOnlyMode(1)
    factory.SetUseMesaClasses(1)
    vtk_overlay = VTKOverlayWindow()
    vtk_overlay.GetRenderWindow().SetOffScreenRendering(1)
    vtk_overlay.set_video_image(image)
    return setup_qt, vtk_overlay, image
