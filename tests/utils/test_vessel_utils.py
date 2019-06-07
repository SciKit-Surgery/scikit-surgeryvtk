# -*- coding: utf-8 -*-

import pytest
import vtk
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sksurgeryvtk.utils.voxelisation_utils as voxelisation_utils
import sksurgeryvtk.utils.vessel_utils as vessel_utils


def test_load_vessel_centrelines_from_file_valid(
        vtk_overlay_with_gradient_image):
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    poly_data, poly_data_mapper = vessel_utils.load_vessel_centrelines(
        input_file)

    actor = vtk.vtkActor()
    actor.SetMapper(poly_data_mapper)
    actor.GetProperty().SetColor(0.0, 0.0, 1.0)
    actor.GetProperty().SetPointSize(50)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()


######################
# TODO: To be moved to the planning app.

class VTKMouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """
    Adds point picker to the interactor.
    """
    def __init__(self, renderer, parent=None):
        """
        Constructor.
        """
        self.AddObserver('LeftButtonPressEvent', self.leftButtonPressEvent)
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.NewPickedActor = None
        self.renderer = renderer

    def leftButtonPressEvent(self, obj, event):
        print('Enters leftButtonPresEvent()')

        clicked_pos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()

        print('clicked pos', clicked_pos)

        picker.Pick(clicked_pos[0], clicked_pos[1], 0, self.renderer)
        self.NewPickedActor = picker.GetActor()

        # If something was picked.
        if self.NewPickedActor:
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(
                    self.LastPickedProperty)

            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)
            self.LastPickedActor = self.NewPickedActor

        self.OnLeftButtonDown()

######################

def test_compute_closest_vessel_centreline_point_for_organ_voxel_valid(
        vtk_overlay_with_gradient_image):
    # Load vessel centrelines and branches.
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info.txt'
    poly_data, poly_data_mapper = vessel_utils.load_vessel_centrelines(
        input_file)
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
                                     colors.grey, opacity=0.2)

    # Load liver model and voxelise it.
    input_file = 'tests/data/vessel_centrelines/liver.vtk'
    liver_voxels, liver_glyph_3d_mapper = voxelisation_utils.voxelise_3d_mesh(
        input_file, [4, 4, 4])

    # Compute the closest vessel centreline point for each organ voxel.
    # vessel_utils.compute_closest_vessel_centreline_point_for_organ_voxels(
    #     poly_data, liver_glyph_3d_mapper)

    liver_actor = vtk.vtkActor()
    liver_actor.SetMapper(liver_glyph_3d_mapper)
    liver_actor.GetProperty().SetColor(1.0, 0.5, 0.5)
    liver_actor.GetProperty().SetOpacity(0.2)
    liver_actor.VisibilityOff()

    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.add_vtk_actor(portal_vein_model.actor)
    widget.add_vtk_actor(hepatic_veins_model.actor)
    widget.add_vtk_actor(arteries_model.actor)
    widget.add_vtk_actor(liver_actor)

    interactor_style = VTKMouseInteractorStyle(widget.get_foreground_renderer())
    widget.GetRenderWindow().GetInteractor().SetInteractorStyle(
        interactor_style)

    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()


def test_load_vessel_centrelines_from_file_invalid_as_empty():
    input_file = 'tests/data/vessel_centrelines/vessel_tree_info_empty.txt'
    with pytest.raises(ValueError):
        vessel_utils.load_vessel_centrelines(input_file)
