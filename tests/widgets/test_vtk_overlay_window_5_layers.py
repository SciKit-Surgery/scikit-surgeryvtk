# -*- coding: utf-8 -*-

import numpy as np
import pytest
import sksurgeryvtk.models.vtk_surface_model as sm


def test_overlay_window_video_0(vtk_overlay_with_gradient_image):
    """
    As of Issue #222: Tests the 'default' or 'legacy' configuration.

    Prior to Issue #222, there were 3 layers:

      - Layer 0: Video
      - Layer 1: VTK models, overlaid on Video
      - Layer 2: Text annotations.

    So, if you changed the opacity of the VTK models, you got naive alpha blending for Augmented Reality (AR).

    For Issue #222, there are now 5 rendering layers. So, by default you should get:

      - widget.get_background_renderer() should return widget.layer_0_renderer
      - widget.get_foreground_renderer() should return widget.layer_1_renderer
      - widget.get_overlay_renderer() should return widget.layer_4_renderer

    and these 3 are the equivalent of the 3 layers that existed prior to Issue #222.
    """
    liver = sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 0.0, 0.0), opacity=0.2)
    tumors = sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (0.0, 1.0, 0.0), opacity=0.2)
    image, vtk_overlay, vtk_std_err, app = vtk_overlay_with_gradient_image
    vtk_overlay.add_vtk_models([liver, tumors])

    vtk_overlay.resize(512, 256)
    vtk_overlay.show()
    vtk_overlay.Render()

    bg_ren = vtk_overlay.get_background_renderer()
    assert bg_ren == vtk_overlay.layer_0_renderer

    fg_ren = vtk_overlay.get_foreground_renderer()
    assert fg_ren == vtk_overlay.layer_1_renderer

    ov_ren = vtk_overlay.get_overlay_renderer()
    assert ov_ren == vtk_overlay.layer_4_renderer

    foreground_actors = fg_ren.GetActors()
    assert foreground_actors.GetNumberOfItems() == 2

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    #app.exec()


def _create_bgr_gradient_image():
    """
    Creates a dummy gradient image for testing only.

    We changed VTKOverlayWindow in Issue #222, to provide 5 layers instead of 3.
    Issue #225 is to fix the channel ordering, as VTK expects RGB, but OpenCV provides BGR.
    """
    width = 512
    height = 256
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            # Make a simple gradient, but BGR, which is what OpenCV would provide.
            if y < height / 3:
                image[y][x][0] = y
            elif y < height * 2 / 3:
                image[y][x][1] = y
            else:
                image[y][x][2] = y
    return image


def _create_rgba_alpha_mask():
    """
    Creates a dummy mask image for testing only.
    """
    width = 512
    height = 256
    cx = width / 2
    cy = height / 2
    image = 255 * np.ones((height, width, 1), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            dist = np.sqrt((y-cy) * (y-cy) + (x-cx) * (x-cx))
            if dist < 40:
                image[y][x][0] = 0
    return image


def test_overlay_window_video_2(setup_vtk_overlay_window_video_only_layer_2):
    """
    As of Issue #222: Tests the first new configuration.

    The background video can be in layer 0, 2, or both, for different visual effects.

    So, with VTKOverlayWindow(video_in_layer_0=False, video_in_layer_2=True) you should have:

      - widget.get_background_renderer() should return widget.layer_2_renderer
      - widget.get_foreground_renderer() should return widget.layer_1_renderer
      - widget.get_overlay_renderer() should return widget.layer_4_renderer

    This will render the video in layer 2, i.e. IN FRONT of the models in layer 1.
    The idea then is that you can set a mask on the video image to use the alpha channel
    to set some of the video pixels to be transparent, so you can 'see through' the video.
    This gives the illusion of peeking through the video, and seeing the models behind
    the video. The mask could also be faded, so you don't get quite such a hard edge.

    Note that "set_video_image" is expecting a BGR (OpenCV) image.
    """
    liver = sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 0.0, 0.0), opacity=0.2)
    tumors = sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (0.0, 1.0, 0.0), opacity=0.2)
    vtk_overlay, vtk_std_err, app = setup_vtk_overlay_window_video_only_layer_2

    mask = _create_rgba_alpha_mask()
    vtk_overlay.set_video_mask(mask)
    image = _create_bgr_gradient_image()
    vtk_overlay.set_video_image(image)
    vtk_overlay.add_vtk_models([liver, tumors])
    vtk_overlay.resize(512, 256)
    vtk_overlay.show()
    vtk_overlay.Render()

    liver.set_opacity(0.4)
    assert liver.get_opacity() == 0.4
    liver.set_opacity(0.2)
    assert liver.get_opacity() == 0.2

    bg_ren = vtk_overlay.get_background_renderer(layer=2)
    assert bg_ren == vtk_overlay.layer_2_renderer

    fg_ren = vtk_overlay.get_foreground_renderer()
    assert fg_ren == vtk_overlay.layer_1_renderer

    ov_ren = vtk_overlay.get_overlay_renderer()
    assert ov_ren == vtk_overlay.layer_4_renderer

    foreground_actors = fg_ren.GetActors()
    assert foreground_actors.GetNumberOfItems() == 2

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    #app.exec()


def test_overlay_window_video_both(setup_vtk_overlay_window_video_both_layer_0_and_2):
    """
    As of Issue #222: Tests the second new configuration.

    The background video can be in layer 0, 2, or both, for different visual effects.

    So, with VTKOverlayWindow(video_in_layer_0=True, video_in_layer_2=True) you should have:

      - widget.get_background_renderer() should return widget.layer_0_renderer containing the video.
      - widget.get_foreground_renderer() should return widget.layer_1_renderer
      - widget.get_overlay_renderer() should return widget.layer_4_renderer

    So, in this test, we are using both video layers and testing putting models in layer 1,
    which is the default layer. So the models appear behind the masked video, but the video
    appears in both layers 0 and 2, so the background behind the models also shows the video.

    In addition, you can retrieve the foreground renderer, specifying the layer, either 1 or 3.
    """
    liver = sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 0.0, 0.0), opacity=0.2)
    tumors = sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (0.0, 1.0, 0.0), opacity=0.2)
    vtk_overlay, vtk_std_err, app = setup_vtk_overlay_window_video_both_layer_0_and_2

    mask = _create_rgba_alpha_mask()
    vtk_overlay.set_video_mask(mask)
    image = _create_bgr_gradient_image()
    vtk_overlay.set_video_image(image)
    vtk_overlay.add_vtk_models([liver, tumors])
    vtk_overlay.resize(512, 256)
    vtk_overlay.show()
    vtk_overlay.Render()

    bg_ren = vtk_overlay.get_background_renderer()
    assert bg_ren == vtk_overlay.layer_0_renderer

    fg_ren = vtk_overlay.get_foreground_renderer()
    assert fg_ren == vtk_overlay.layer_1_renderer

    ov_ren = vtk_overlay.get_overlay_renderer()
    assert ov_ren == vtk_overlay.layer_4_renderer

    foreground_actors = fg_ren.GetActors()
    assert foreground_actors.GetNumberOfItems() == 2

    fg_ren = vtk_overlay.get_foreground_renderer(layer=1)
    assert fg_ren == vtk_overlay.layer_1_renderer

    fg_ren = vtk_overlay.get_foreground_renderer(layer=3)
    assert fg_ren == vtk_overlay.layer_3_renderer

    fg_ren = vtk_overlay.get_foreground_renderer(layer=4)
    assert fg_ren == vtk_overlay.layer_4_renderer

    with pytest.raises(ValueError):
        fg_ren = vtk_overlay.get_foreground_renderer(layer=0)

    with pytest.raises(ValueError):
        fg_ren = vtk_overlay.get_foreground_renderer(layer=2)

    with pytest.raises(ValueError):
        fg_ren = vtk_overlay.get_foreground_renderer(layer=5)

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    #app.exec()


def test_overlay_window_combined_ar_look(setup_vtk_overlay_window_video_only_layer_2):
    """
    As of Issue #222: Tests the third new configuration.

    Given all the options described above, in this test we aim for:

      - VTKOverlayWindow(video_in_layer_0=False, video_in_layer_2=True) to put video in layer 2.
      - we apply a mask to the video to give the impression of seeing inside the model
      - we add internal anatomy (e.g. tumour) behind the video in layer 2.
      - we add external anatomy (e.g. liver) in front of the video in layer 2.
      - we render the external anatomy as outline, and surface.
    """
    liver = sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 0.0, 0.0), opacity=0.2, outline=True)
    tumors = sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (0.0, 1.0, 0.0), opacity=0.2)
    vtk_overlay, vtk_std_err, app = setup_vtk_overlay_window_video_only_layer_2

    mask = _create_rgba_alpha_mask()
    vtk_overlay.set_video_mask(mask)
    image = _create_bgr_gradient_image()
    vtk_overlay.set_video_image(image)
    vtk_overlay.add_vtk_models([tumors], layer=1)
    vtk_overlay.add_vtk_models([liver], layer=3)
    vtk_overlay.resize(512, 256)
    vtk_overlay.show()
    vtk_overlay.Render()

    bg_ren = vtk_overlay.get_background_renderer(layer=2)
    assert bg_ren == vtk_overlay.layer_2_renderer

    fg_ren = vtk_overlay.get_foreground_renderer(layer=1)
    assert fg_ren == vtk_overlay.layer_1_renderer

    foreground_actors = fg_ren.GetActors()
    assert foreground_actors.GetNumberOfItems() == 1

    fg_ren = vtk_overlay.get_foreground_renderer(layer=3)
    assert fg_ren == vtk_overlay.layer_3_renderer

    foreground_actors = fg_ren.GetActors()
    assert foreground_actors.GetNumberOfItems() == 2 # i.e. surface AND outline.

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    #app.exec()