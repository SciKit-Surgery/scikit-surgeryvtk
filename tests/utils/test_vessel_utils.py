# -*- coding: utf-8 -*-

import pytest
import vtk
import sksurgeryvtk.utils.voxelisation_utils as voxelisation_utils
import sksurgeryvtk.utils.vessel_utils as vessel_utils


def test_load_vessel_centrelines_from_file_valid(
        vtk_overlay_with_gradient_image):
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    _, vessel_poly_data_mapper = \
        vessel_utils.load_vessel_centrelines(input_file)

    actor = vtk.vtkActor()
    actor.SetMapper(vessel_poly_data_mapper)
    actor.GetProperty().SetColor(0.0, 0.0, 1.0)
    actor.GetProperty().SetPointSize(50)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()


def test_compute_closest_vessel_centreline_point_for_organ_voxel_valid():
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    vessel_poly_data, _ = vessel_utils.load_vessel_centrelines(input_file)

    # Load liver model and voxelise it.
    input_file = 'tests/data/vessel_centrelines/liver.vtk'
    _, liver_glyph_3d_mapper = voxelisation_utils.voxelise_3d_mesh(
        input_file, [4, 4, 4])

    # Compute the closest vessel centreline point for each organ voxel.
    vessel_utils.compute_closest_vessel_centreline_point_for_organ_voxels(
        vessel_poly_data, liver_glyph_3d_mapper)


def test_load_vessel_centrelines_from_file_invalid_as_empty():
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info_empty.txt'

    with pytest.raises(ValueError):
        vessel_utils.load_vessel_centrelines(input_file)


def test_compute_closest_vessel_centreline_point_valid():
    poly_data = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.InsertNextPoint([0.0, 0.0, 0.0])
    points.InsertNextPoint([1.0, 1.0, 1.0])
    poly_data.SetPoints(points)

    assert vessel_utils.compute_closest_vessel_centreline_point(poly_data,
                                                         [0.0, 0.1, 0.1]) \
        == 0


def test_compute_closest_vessel_centreline_point_invalid_as_point_not_3d():
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    vessel_poly_data, _ = vessel_utils.load_vessel_centrelines(input_file)

    with pytest.raises(ValueError):
        vessel_utils.compute_closest_vessel_centreline_point(vessel_poly_data,
                                                             [1, 2])


def test_get_branch_valid():
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    vessel_poly_data, _ = vessel_utils.load_vessel_centrelines(input_file)

    assert vessel_utils.get_branch(vessel_poly_data, 21) == 1
