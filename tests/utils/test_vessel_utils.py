# -*- coding: utf-8 -*-

import pytest
import vtk
import numpy as np
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sksurgeryvtk.utils.voxelisation_utils as voxelisation_utils
import sksurgeryvtk.utils.vessel_utils as vessel_utils


def test_load_vessel_centrelines_from_file_valid(
        vtk_overlay_with_gradient_image):
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    poly_data, poly_data_mapper = vessel_utils.load_vessel_centrelines(input_file)

    actor = vtk.vtkActor()
    actor.SetMapper(poly_data_mapper)
    actor.GetProperty().SetColor(0.0, 0.0, 1.0)
    actor.GetProperty().SetPointSize(50)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()

def test_compute_distance_from_vessel_centrelines_to_organ_valid(
        vtk_overlay_with_gradient_image):
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    poly_data, poly_data_mapper = vessel_utils.load_vessel_centrelines(input_file)
    actor = vtk.vtkActor()
    actor.SetMapper(poly_data_mapper)
    actor.GetProperty().SetColor(0.0, 0.0, 1.0)
    actor.GetProperty().SetPointSize(50)

    # Load vessel models.
    input_file = 'tests/data/vessel_centrelines/portal_vein.vtk'
    portal_vein_model = VTKSurfaceModel(input_file,
                                        colors.blue, opacity=0.2)
    input_file = 'tests/data/vessel_centrelines/hepatic_veins.vtk'
    hepatic_veins_model = VTKSurfaceModel(input_file,
                                          colors.yellow, opacity=0.2)
    input_file = 'tests/data/vessel_centrelines/arteries.vtk'
    arteries_model = VTKSurfaceModel(input_file,
                                     colors.green, opacity=0.2)

    # Load liver model and voxelise it.
    input_file = 'tests/data/vessel_centrelines/liver.vtk'
    _, glyph_3d_mapper = voxelisation_utils.voxelise_3d_mesh(input_file,
                                                             [100, 100, 100],
                                                             [1, 1, 1])
    liver_actor = vtk.vtkActor()
    liver_actor.SetMapper(glyph_3d_mapper)
    liver_actor.GetProperty().SetColor(1.0, 0.5, 0.5)

    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.add_vtk_actor(portal_vein_model.actor)
    widget.add_vtk_actor(hepatic_veins_model.actor)
    widget.add_vtk_actor(arteries_model.actor)
    widget.add_vtk_actor(liver_actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    app.exec_()

# def test_load_vessel_centrelines_from_file_invalid_as_empty():
#     input_file = 'tests/data/vessel_centrelines/vessel_centrelines_empty.dat'
#     with pytest.raises(ValueError):
#         vu.load_vessel_centrelines(input_file)
