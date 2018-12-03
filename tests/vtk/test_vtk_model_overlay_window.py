import pytest
import numpy as np

def test_VTK_render_window_settings(vtk_overlay):
    assert vtk_overlay._RenderWindow.GetStereoRender()
    assert vtk_overlay._RenderWindow.GetStereoCapableWindow()
    assert vtk_overlay._RenderWindow.GetAlphaBitPlanes()
    assert vtk_overlay._RenderWindow.GetMultiSamples() == 0

def test_VTK_foreground_render_settings(vtk_overlay):
    assert vtk_overlay.foreground_renderer.GetLayer() == 1
    assert vtk_overlay.foreground_renderer.GetUseDepthPeeling()
    
def test_image_importer(vtk_overlay):

    width, height, _ = vtk_overlay.input.frame.shape
    expected_extent = (0, height - 1, 0, width - 1, 0, 0)
    
    assert vtk_overlay.image_importer.GetDataExtent() == expected_extent
    assert vtk_overlay.image_importer.GetDataScalarTypeAsString() == "unsigned char"
    assert vtk_overlay.image_importer.GetNumberOfScalarComponents() == 3
    
def test_VTK_background_render_settings(vtk_overlay):
    assert vtk_overlay.background_renderer.GetLayer() == 0
    assert vtk_overlay.background_renderer.GetInteractive() == False

def test_frame_pixels(vtk_overlay):
    """Test pixel values in the frame to make sure they are as expected."""
       
    pixel = vtk_overlay.rgb_frame[0,0,:]
    expected_pixel = [1,1,1]
    assert np.array_equal(pixel, expected_pixel)

def test_stereo_setting(vtk_overlay):
    vtk_overlay.set_stereo_left()
    assert vtk_overlay._RenderWindow.GetStereoTypeAsString() == "Left"

    vtk_overlay.set_stereo_right()
    assert vtk_overlay._RenderWindow.GetStereoTypeAsString() == "Right"

def test_numpy_exporter(vtk_overlay):
    # Setting up the numpy exporter should set the image filter input to
    # the vtk overlay's _RenderWindow.
    vtk_overlay.setup_numpy_exporter()
    assert vtk_overlay.vtk_win_to_img_filter.GetInput() == vtk_overlay._RenderWindow

    vtk_overlay.convert_scene_to_numpy_array()

    # The output numpy array should have the same dimensions as the _RenderWindow
    ren_win_size = vtk_overlay._RenderWindow.GetSize()
    expected_shape = (ren_win_size[0], ren_win_size[1], 3)
    assert vtk_overlay.output_frames[0].shape == expected_shape