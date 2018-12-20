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


@pytest.fixture(scope="function")
def setup_vtk_err(setup_qt):
    """ Used to send VTK errors to file instead of screen. """
    err_out = vtk.vtkFileOutputWindow()
    err_out.SetFileName('tests/output/vtk.err.txt')
    vtk_std_err = vtk.vtkOutputWindow()
    vtk_std_err.SetInstance(err_out)
    return vtk_std_err, setup_qt


@pytest.fixture(scope="function")
def setup_vtk_offscreen(setup_vtk_err):
    """ Used to ensure VTK renders to offscreen window. """
    vtk_std_err, setup_qt = setup_vtk_err

    if not setup_qt.screens():
        six.print_("Early exit, as no screen available.")
        return None, None, None

    factory = vtk.vtkGraphicsFactory()
    factory.SetOffScreenOnlyMode(0)
    factory.SetUseMesaClasses(0)
    vtk_overlay = VTKOverlayWindow()
    vtk_overlay.GetRenderWindow().SetOffScreenRendering(0)
    return vtk_overlay, vtk_std_err, setup_qt


# Note: These windows will persist while all unit tests run.
#       Don't waste time trying to debug why you see >1 windows.
@pytest.fixture(scope="function")
def vtk_overlay(setup_vtk_offscreen):
    """ Creates a VTKOverlayWindow with blank background image. """
    vtk_overlay, vtk_std_err, setup_qt = setup_vtk_offscreen

    if vtk_overlay is None:
        return None, vtk_std_err, setup_qt

    image = np.ones((150, 100, 3), dtype=np.uint8)
    vtk_overlay.set_video_image(image)

    return vtk_overlay, vtk_std_err, setup_qt


# Note: These windows will persist while all unit tests run.
#       Don't waste time trying to debug why you see >1 windows.
@pytest.fixture(scope="function")
def vtk_overlay_with_gradient_image(setup_vtk_offscreen):
    """ Creates a VTKOverlayWindow with gradient image. """
    vtk_overlay, vtk_std_err, setup_qt = setup_vtk_offscreen

    if vtk_overlay is None:
        return None, None, vtk_std_err, setup_qt

    width = 512
    height = 256
    image = np.ones((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            image[y][x][0] = y
            image[y][x][1] = y
            image[y][x][2] = y
    vtk_overlay.set_video_image(image)
    return image, vtk_overlay, vtk_std_err, setup_qt
