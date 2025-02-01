# -*- coding: utf-8 -*-

import os
import platform

import cv2
import numpy as np
import pytest
from sksurgeryimage.utilities.utilities import are_similar
import sksurgeryvtk.models.vtk_surface_model as sm

# Shared skipif maker for all modules
skip_pytest_in_linux = pytest.mark.skipif(
    platform.system() == "Linux",
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'due to issues with VTK pipelines and pyside workflows with Class Inheritance'
)


@skip_pytest_in_linux
def test_rendering_zbuffer(setup_vtk_zbuffer_window):
    """
    To test rendering z-buffer type images.
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this method.
    """
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_zbuffer_window

    liver = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0))]

    widget.add_vtk_models(liver,layer=0)
    widget.get_renderer(layer=0).ResetCamera()
    widget.show()

    # Check camera and clipping range.
    position = widget.get_camera(layer=0).GetPosition()
    focal_point = widget.get_camera(layer=0).GetFocalPoint()
    range = np.abs(position[2] - focal_point[2])
    widget.set_clipping_range(range-50, range+50)

    widget.save_scene_to_file("tests/output/rendering-zbuffer.png")

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    #_pyside_qt_app.exec()
    widget.close()
