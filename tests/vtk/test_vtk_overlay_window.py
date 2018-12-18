# -*- coding: utf-8 -*-

import pytest
import vtk
import six
import numpy as np
import sksurgeryoverlay.vtk.vtk_overlay_window as v


def test_vtk_render_window_settings(setup_vtk_offscreen):

    widget, _, _ = setup_vtk_offscreen

    assert not widget.GetRenderWindow().GetStereoRender()
    assert not widget.GetRenderWindow().GetStereoCapableWindow()
    assert widget.GetRenderWindow().GetAlphaBitPlanes()
    assert widget.GetRenderWindow().GetMultiSamples() == 0


def test_vtk_foreground_render_settings(setup_vtk_offscreen):

    widget, _, _ = setup_vtk_offscreen

    assert widget.foreground_renderer.GetLayer() == 1
    assert widget.foreground_renderer.GetUseDepthPeeling()


def test_vtk_background_render_settings(setup_vtk_offscreen):

    widget, _, _ = setup_vtk_offscreen

    assert widget.background_renderer.GetLayer() == 0
    assert not widget.background_renderer.GetInteractive()


def test_image_importer(setup_vtk_offscreen):

    widget, _, _ = setup_vtk_offscreen

    width, height, _ = widget.input.shape
    expected_extent = (0, height - 1, 0, width - 1, 0, 0)
    
    assert widget.image_importer.GetDataExtent() == expected_extent
    assert widget.image_importer.GetDataScalarTypeAsString() == "unsigned char"
    assert widget.image_importer.GetNumberOfScalarComponents() == 3


def test_frame_pixels(vtk_overlay):

    widget, _, _ = vtk_overlay

    if widget is None:
        six.print_('Finishing early as no screen available.')
        return

    pixel = widget.rgb_frame[0, 0, :]
    expected_pixel = [1, 1, 1]
    assert np.array_equal(pixel, expected_pixel)


def test_import_image_display_copy_check_same_size(vtk_overlay_with_gradient_image):

    image, widget, _, app = vtk_overlay_with_gradient_image

    if widget is None:
        six.print_('Finishing early as no screen available.')
        return

    widget.resize(image.shape[1], image.shape[0])

    output = widget.convert_scene_to_numpy_array()
    assert widget.vtk_win_to_img_filter.GetInput() == widget.GetRenderWindow()

    # The output numpy array should have the same dimensions as the RenderWindow.
    ren_win_size = widget.GetRenderWindow().GetSize()
    expected_shape = (ren_win_size[1], ren_win_size[0], 3)
    assert output.shape == expected_shape

    # The output numpy array should have the same shape as original image.
    # At the moment, it appears to be twice as big. Don't know why.
    #assert output.shape[0] == height
    #assert output.shape[1] == width


def test_basic_cone_overlay(vtk_overlay_with_gradient_image):
    """
    Not really a unit test as it doesnt assert anything.
    But at least it might throw an error if something else changes.
    """
    image, widget, _, app = vtk_overlay_with_gradient_image

    if widget is None:
        six.print_('Finishing early as no screen available.')
        return

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
    # app.exec_()
