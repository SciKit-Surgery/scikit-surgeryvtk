# -*- coding: utf-8 -*-

import pytest
from PySide2.QtWidgets import QApplication
from collections import namedtuple
import numpy as np
from sksurgeryoverlay.vtk.vtk_overlay_window import VTKOverlayWindow


@pytest.fixture(scope="session")
def setup_qt():
    """ Create the QT application"""
    app = QApplication([])
    return app


@pytest.fixture(scope="module")
def vtk_overlay(setup_qt):
    """
    Create a vtk_overlay object that will be used for all tests.
    """
    # Mock the VideoSource class
    struct = namedtuple("struct", "frame")
    frame = np.ones((150, 100, 3), dtype=np.uint8)
    fake_source = struct(frame)
    vtk_overlay = VTKOverlayWindow(fake_source)
    return setup_qt, vtk_overlay


@pytest.fixture(scope="module")
def vtk_overlay_from_generated_image(setup_qt):
    struct = namedtuple("struct", "frame")
    width = 512
    height = 256
    frame = np.ones((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            frame[y][x][0] = y
            frame[y][x][1] = y
            frame[y][x][2] = y
    fake_source = struct(frame)
    vtk_overlay = VTKOverlayWindow(fake_source)
    return setup_qt, width, height, vtk_overlay
