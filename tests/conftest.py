# -*- coding: utf-8 -*-

import platform

import numpy as np
import pytest
import vtk
from PySide6.QtWidgets import QApplication

from sksurgeryvtk.widgets.vtk_interlaced_stereo_window import VTKStereoInterlacedWindow
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from sksurgeryvtk.widgets.vtk_zbuffer_window import VTKZBufferWindow


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
    Sets `init_widget_flag` to False on Linux, and True on Windows and Mac.
    When init_widget_flag==True, the VTKOverlayWindow constructor calls
    `self.Initialize` and `self.Start` when creating the widget.
    """

    vtk_std_err, setup_qt = setup_vtk_err

    if platform.system() == 'Linux':
        init_widget_flag = False
    else:
        init_widget_flag = True

    vtk_overlay = VTKOverlayWindow(offscreen=False, init_widget=init_widget_flag)
    return vtk_overlay, vtk_std_err, setup_qt


@pytest.fixture(scope="function")
def setup_vtk_zbuffer_window(setup_vtk_err):
    """
    Sets `init_widget_flag` to False on Linux, and True on Windows and Mac.
    When init_widget_flag==True, the VTKZBufferWindow constructor calls
    `self.Initialize` and `self.Start` when creating the widget.
    """

    vtk_std_err, setup_qt = setup_vtk_err

    if platform.system() == 'Linux':
        init_widget_flag = False
    else:
        init_widget_flag = True

    vtk_overlay = VTKZBufferWindow(offscreen=False, init_widget=init_widget_flag)
    return vtk_overlay, vtk_std_err, setup_qt


@pytest.fixture(scope="function")
def setup_vtk_overlay_window_no_init(setup_vtk_err):
    """
    Similar to the above function, except init_widget=False, so
    `self.Initialize` and `self.Start` are not called in the VTKOverlayWindow constructor.
    """

    vtk_std_err, setup_qt = setup_vtk_err

    vtk_overlay = VTKOverlayWindow(offscreen=False, init_widget=False)
    return vtk_overlay, vtk_std_err, setup_qt


def _create_gradient_image():
    """
    Creates a dummy gradient image for testing only.
    """
    width = 512
    height = 256
    image = np.ones((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            image[y][x][0] = y
            image[y][x][1] = y
            image[y][x][2] = y
    return image


# Note: These windows will persist while all unit tests run.
#       Don't waste time trying to debug why you see >1 windows.
@pytest.fixture(scope="function")
def vtk_overlay_with_gradient_image(setup_vtk_overlay_window):
    """ Creates a VTKOverlayWindow with gradient image. """

    vtk_overlay, vtk_std_err, setup_qt = setup_vtk_overlay_window
    image = _create_gradient_image()
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


@pytest.fixture(scope="function")
def setup_vtk_overlay_window_video_only_layer_2(setup_vtk_err):
    """
    Sets `init_widget_flag` to False on Linux, and True on Windows and Mac.
    When init_widget_flag==True, the VTKOverlayWindow constructor calls
    `self.Initialize` and `self.Start` when creating the widget.

    As of Issue #222: And also sets video_in_layer_0=False and video_in_layer_2=True
    in VTKOverlayWindow constructor. See VTKOverlayWindow docstring for explanation.
    """

    vtk_std_err, setup_qt = setup_vtk_err

    if platform.system() == 'Linux':
        init_widget_flag = False
    else:
        init_widget_flag = True

    vtk_overlay = VTKOverlayWindow(offscreen=False,
                                   init_widget=init_widget_flag,
                                   video_in_layer_0=False,
                                   video_in_layer_2=True
                                   )
    image = _create_gradient_image()
    vtk_overlay.set_video_image(image)
    return vtk_overlay, vtk_std_err, setup_qt


@pytest.fixture(scope="function")
def setup_vtk_overlay_window_video_both_layer_0_and_2(setup_vtk_err):
    """
    Sets `init_widget_flag` to False on Linux, and True on Windows and Mac.
    When init_widget_flag==True, the VTKOverlayWindow constructor calls
    `self.Initialize` and `self.Start` when creating the widget.

    As of Issue #222: And also sets video_in_layer_0=True and video_in_layer_2=True
    in VTKOverlayWindow constructor. See VTKOverlayWindow docstring for explanation.
    """

    vtk_std_err, setup_qt = setup_vtk_err

    if platform.system() == 'Linux':
        init_widget_flag = False
    else:
        init_widget_flag = True

    vtk_overlay = VTKOverlayWindow(offscreen=False,
                                   init_widget=init_widget_flag,
                                   video_in_layer_0=True,
                                   video_in_layer_2=True
                                   )
    image = _create_gradient_image()
    vtk_overlay.set_video_image(image)
    return vtk_overlay, vtk_std_err, setup_qt
