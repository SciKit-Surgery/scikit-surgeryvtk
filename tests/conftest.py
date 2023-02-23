# -*- coding: utf-8 -*-

import platform

import numpy as np
import pytest
import vtk
from PySide6.QtWidgets import QApplication

from sksurgeryvtk.widgets.vtk_interlaced_stereo_window import VTKStereoInterlacedWindow
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow


@pytest.fixture(scope="session")
def setup_qt():
    """ Create the QT application. """
    app = QApplication([])
    return app


@pytest.fixture(scope="session")
def setup_vtk_err(setup_qt):
    """ Used to send VTK errors to file instead of screen. """

    err_out = vtk.vtkFileOutputWindow()
    err_out.SetFileName('tests/output/vtk.err.txt')
    vtk_std_err = vtk.vtkOutputWindow()
    vtk_std_err.SetInstance(err_out)
    return vtk_std_err, setup_qt


@pytest.fixture(scope="function")
def setup_vtk_overlay_window(setup_vtk_err):
    """
    This function so you can select offscreen or not, while debugging.

    `init_widget_flag` is set to false `init_widget_flag` when testing in Linux OS machines.
    Otherwise, `init_widget_flag = True`, calling `self.Initialize` and `self.Start` in the init function of
        VTKOverlayWindow class
    """

    vtk_std_err, setup_qt = setup_vtk_err

    if platform.system() == 'Linux':
        init_widget_flag = False
    else:
        init_widget_flag = True

    vtk_overlay = VTKOverlayWindow(offscreen=False, init_widget=init_widget_flag)
    return vtk_overlay, vtk_std_err, setup_qt


@pytest.fixture(scope="function")
def setup_vtk_overlay_window_no_init(setup_vtk_err):
    """ This function so you can select offscreen or not, while debugging. """

    vtk_std_err, setup_qt = setup_vtk_err

    vtk_overlay = VTKOverlayWindow(offscreen=False, init_widget=False)
    return vtk_overlay, vtk_std_err, setup_qt


# Note: These windows will persist while all unit tests run.
#       Don't waste time trying to debug why you see >1 windows.
@pytest.fixture(scope="function")
def vtk_overlay_with_gradient_image(setup_vtk_overlay_window):
    """ Creates a VTKOverlayWindow with gradient image. """

    vtk_overlay, vtk_std_err, setup_qt = setup_vtk_overlay_window

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


@pytest.fixture(scope="function")
def vtk_interlaced_stereo_window(setup_vtk_err):
    """ Used to ensure VTK renders to off screen vtk_interlaced_stereo_window. """

    vtk_std_err, setup_qt = setup_vtk_err

    if platform.system() == 'Linux':
        init_widget_flag = False
    else:
        init_widget_flag = True

    vtk_interlaced = VTKStereoInterlacedWindow(offscreen=False, init_widget=init_widget_flag)
    return vtk_interlaced, vtk_std_err, setup_qt
