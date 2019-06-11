# -*- coding: utf-8 -*-

import vtk
import sksurgeryvtk.utils.voxelisation_utils as vu


def test_voxelisation_of_3d_mesh_valid(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/vessel_centrelines/liver.vtk'
    _, glyph_3d_mapper = vu.voxelise_3d_mesh(input_file, [1, 1, 1])
    actor = vtk.vtkActor()
    actor.SetMapper(glyph_3d_mapper)
    actor.GetProperty().SetColor(1.0, 0.5, 0.5)
    image, widget, _, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(actor)
    widget.show()

    # Uncomment if you want to check the voxelised model.
    # app.exec_()


