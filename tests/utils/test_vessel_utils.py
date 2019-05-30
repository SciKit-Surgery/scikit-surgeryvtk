# -*- coding: utf-8 -*-

import pytest
import vtk
import numpy as np
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sys
import os

import sksurgeryvtk.utils.vessel_utils as vu


def test_load_vessel_centrelines_from_file_valid(
        vtk_overlay_with_gradient_image):
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    poly_data, poly_data_mapper = vu.load_vessel_centrelines(input_file)

    actor = vtk.vtkActor()
    actor.SetMapper(poly_data_mapper)
    actor.GetProperty().SetColor(0.0, 0.0, 1.0)
    actor.GetProperty().SetPointSize(50)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()

# def test_load_vessel_centrelines_from_file_invalid_as_empty():
#     input_file = 'tests/data/vessel_centrelines/vessel_centrelines_empty.dat'
#     with pytest.raises(ValueError):
#         vu.load_vessel_centrelines(input_file)
