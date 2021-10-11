# -*- coding: utf-8 -*-

import pytest
import vtk
import numpy as np
import sksurgeryvtk.utils.matrix_utils as mu
import sksurgeryvtk.models.vtk_surface_model as sm


def test_match_sppa(setup_vtk_overlay_window):

    vtk_overlay, vtk_std_err, app = setup_vtk_overlay_window

    intrinsics = np.loadtxt('tests/data/match_surface_plus_probe_app/spp_intrinsics.txt')
    l2c = np.loadtxt('tests/data/match_surface_plus_probe_app/spp_liver2camera.txt')
    ws = np.loadtxt('tests/data/match_surface_plus_probe_app/spp_window_size.txt')
    cr = np.loadtxt('tests/data/match_surface_plus_probe_app/spp_clipping_range.txt')
    models = [sm.VTKSurfaceModel('tests/data/match_surface_plus_probe_app/spp_liver_normalised.vtk', (0.9, 0.4, 0.4))]

    # This simple adds meshes to the right renderer. In this case, just 1 liver.
    vtk_overlay.add_vtk_models(models)

    # As we are testing a programmatically driven rendering pipeline,
    # the size of the window is known. It will be the size we calibrated with.
    vtk_overlay.setFixedSize(ws[0], ws[1])

    # The VTKOverlayWindow must have the correct size background image
    # as the openGL scaling takes into account the difference between
    # an image that you are overlaying on, and the ACTUAL window size.
    # So, if you aren't actually doing an overlay, you should still
    # provide the correct size (meaning, 'as if you had a video image',
    # or 'the size of video image, you have calibrated against') to
    # match the intrinsic parameters. Here, it's black background.
    background_image = np.zeros((int(ws[1]), int(ws[0]), 3))
    vtk_overlay.set_video_image(background_image)

    # In the surface_plus_probe_app.py, the camera is ALWAYS at origin.
    # (at the time of writing this comment).
    vtk_overlay.set_camera_pose(np.eye(4))

    # The surface_plus_probe_app.py, outputs the liver-to-camera
    # so we need to apply it to the model, which moves the model, not camera.
    vtk_matrix = mu.create_vtk_matrix_from_numpy(l2c)
    models[0].actor.PokeMatrix(vtk_matrix)

    # Also, set the same clipping range, just because we have it available.
    cam = vtk_overlay.get_foreground_camera()
    cam.SetClippingRange(cr[0], cr[1])

    # Now we should be able to render as per the example from surface_pluse_probe app.
    vtk_overlay.show()

    # This method RELIES on the vtk rendering environment being
    # correctly initialised, and the interaction between Qt and VTK is
    # a bit wierd, as when a widget is placed on screen, (at least on a Mac),
    # the widget is resized multiple times, and the vtkRenderWindow eventually
    # resizes to match the Qt window. So, you need the vtk_over.show() above
    # at least once BEFORE the line below. Then when you set/force the intrinsics
    # in the line below, then the size of the window is correct, and calculations work.
    vtk_overlay.set_camera_matrix(intrinsics)

    #app.exec_()


