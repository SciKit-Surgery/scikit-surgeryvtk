# -*- coding: utf-8 -*-

import pytest
import vtk
import numpy as np
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sys
import os

import sksurgeryvtk.utils.voxelisation_utils as vu


def test_voxelisation_of_3d_mesh(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/models/spacefighter.stl'

    # Load stl file.
    reader = vtk.vtkSTLReader()
    reader.SetFileName(input_file)
    reader.Update()

    poly_data = vtk.vtkPolyData()
    poly_data.DeepCopy(reader.GetOutput())

    glyph_3d_mapper = vu.voxelise_3d_mesh(poly_data, 200, 200, 200)
    actor = vtk.vtkActor()
    actor.SetMapper(glyph_3d_mapper)
    actor.GetProperty().SetColor(0.0, 1.0, 0.0)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()


def test_voxelisation_of_3d_mesh_from_file(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/models/spacefighter.stl'
    glyph_3d_mapper = vu.voxelise_3d_mesh_from_file(input_file, 200, 200, 200)
    actor = vtk.vtkActor()
    actor.SetMapper(glyph_3d_mapper)
    actor.GetProperty().SetColor(0.0, 1.0, 0.0)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()
