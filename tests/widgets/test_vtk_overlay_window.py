# -*- coding: utf-8 -*-

import vtk
import numpy as np
import sksurgeryvtk.models.vtk_point_model as pm


def test_vtk_render_window_settings(setup_vtk_overlay_window):

    widget, _, _, _ = setup_vtk_overlay_window

    assert not widget.GetRenderWindow().GetStereoRender()
    assert not widget.GetRenderWindow().GetStereoCapableWindow()
    #assert widget.GetRenderWindow().GetAlphaBitPlanes()
    assert widget.GetRenderWindow().GetMultiSamples() == 0


def test_vtk_foreground_render_settings(setup_vtk_overlay_window):

    widget, _, _, _= setup_vtk_overlay_window

    assert widget.foreground_renderer.GetLayer() == 1
    assert widget.foreground_renderer.GetUseDepthPeeling()


def test_vtk_background_render_settings(setup_vtk_overlay_window):

    widget, _, _, _ = setup_vtk_overlay_window

    assert widget.background_renderer.GetLayer() == 0
    assert not widget.background_renderer.GetInteractive()


def test_image_importer(setup_vtk_overlay_window):

    widget, _, _, _ = setup_vtk_overlay_window

    width, height, _ = widget.input.shape
    expected_extent = (0, height - 1, 0, width - 1, 0, 0)

    assert widget.image_importer.GetDataExtent() == expected_extent
    assert widget.image_importer.GetDataScalarTypeAsString() == "unsigned char"
    assert widget.image_importer.GetNumberOfScalarComponents() == 3


def test_frame_pixels(setup_vtk_overlay_window):

    widget, _, _, _ = setup_vtk_overlay_window

    pixel = widget.rgb_frame[0, 0, :]
    expected_pixel = [1, 1, 1]
    assert np.array_equal(pixel, expected_pixel)


def test_basic_cone_overlay(vtk_overlay_with_gradient_image):
    """
    Not really a unit test as it doesnt assert anything.
    But at least it might throw an error if something else changes.
    """
    image, widget, _, _, app = vtk_overlay_with_gradient_image

    widget.resize(image.shape[1], image.shape[0])

    cone = vtk.vtkConeSource()
    cone.SetResolution(60)
    cone.SetCenter(-2, 0, 0)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cone.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    widget.add_vtk_actor(actor)

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    #app.exec_()


def test_point_set_overlay(vtk_overlay):

    widget, _, _, app = vtk_overlay

    points = np.zeros((4, 3), dtype=np.float)
    points[1][0] = 1
    points[2][1] = 1
    points[3][2] = 1
    colours = np.zeros((4, 3), dtype=np.byte)
    colours[0][0] = 255
    colours[0][1] = 255
    colours[0][2] = 255
    colours[1][0] = 255
    colours[2][1] = 255
    colours[3][2] = 255

    vtk_models = [pm.VTKPointModel(points, colours)]
    widget.add_vtk_models(vtk_models)

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    #app.exec_()
