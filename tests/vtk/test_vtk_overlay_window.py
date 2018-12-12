# -*- coding: utf-8 -*-

import pytest
import numpy as np


def test_vtk_render_window_settings(vtk_overlay):

    app, widget = vtk_overlay
    widget.Initialize()
    widget.Start()
    widget.show()

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit.
    # app.exec_()

    assert not widget.GetRenderWindow().GetStereoRender()
    assert not widget.GetRenderWindow().GetStereoCapableWindow()
    assert widget.GetRenderWindow().GetAlphaBitPlanes()
    assert widget.GetRenderWindow().GetMultiSamples() == 0


def test_vtk_foreground_render_settings(vtk_overlay):

    app, widget = vtk_overlay

    assert widget.foreground_renderer.GetLayer() == 1
    assert widget.foreground_renderer.GetUseDepthPeeling()


def test_vtk_background_render_settings(vtk_overlay):

    app, widget = vtk_overlay

    assert widget.background_renderer.GetLayer() == 0
    assert not widget.background_renderer.GetInteractive()


def test_image_importer(vtk_overlay):

    app, widget = vtk_overlay
    width, height, _ = widget.input.frame.shape
    expected_extent = (0, height - 1, 0, width - 1, 0, 0)
    
    assert widget.image_importer.GetDataExtent() == expected_extent
    assert widget.image_importer.GetDataScalarTypeAsString() == "unsigned char"
    assert widget.image_importer.GetNumberOfScalarComponents() == 3


def test_frame_pixels(vtk_overlay):

    app, widget = vtk_overlay

    pixel = widget.rgb_frame[0, 0, :]
    expected_pixel = [1, 1, 1]
    assert np.array_equal(pixel, expected_pixel)


def test_import_image_display_copy_check_same(vtk_overlay_from_generated_image):
    app, width, height, widget = vtk_overlay_from_generated_image
    widget.Initialize()
    widget.Start()
    widget.show()
    widget.Render()
    widget.resize(width, height)
    widget.convert_scene_to_numpy_array()
    assert widget.vtk_win_to_img_filter.GetInput() == widget.GetRenderWindow()

    # The output numpy array should have the same dimensions as the RenderWindow.
    # Currently it doesnt have the same size as the original image.
    ren_win_size = widget.GetRenderWindow().GetSize()
    expected_shape = (ren_win_size[1], ren_win_size[0], 3)
    assert widget.output_frames[0].shape == expected_shape
