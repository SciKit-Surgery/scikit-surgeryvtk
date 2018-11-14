import pytest
import cv2
import numpy as np
from collections import namedtuple

from sksurgeryoverlay.vtk.vtk_overlay_window import VTKOverlayWindow

import logging
import cv2


@pytest.fixture
def fake_video_source(setup_qt):
    struct = namedtuple("struct", "frames")
    frames = [np.ones((100,100,3), dtype=np.uint8), np.ones((100,100,3), dtype=np.uint8)]
    source = struct(frames)

    return source

def test_vtk_overlay(fake_video_source):
    
    vtk_overlay = VTKOverlayWindow(fake_video_source, 0)

    assert True



# @pytest.fixture(scope="module")
# def video_file_source(setup_qt):
#     """ Setup/teardown a video file for subsequent tests"""
#     video_filename = 'test_video.avi'
    
#     video_file_source.frames = np.ones((100,100,3), dtype=np.uint8)
#     return video_file_source
#     # create_video_file(video_filename)
#     # yield video_filename
#     # remove_video_file(video_filename)
    
# @pytest.fixture(scope="module")
# def vtk_window(video_file_source):
#     """Create a vtkOverlayWindow for use in all tests"""
#     print("Input Video: ", video_file_source)
#     vtk_window = VTKOverlayWindow(video_file_source, 0)

#     yield vtk_window
#     vtk_window.background_capture_source.release()
#     vtk_window.stop_interactor()

# def test_VTK_render_window_settings(vtk_window):
#     assert vtk_window._RenderWindow.GetStereoRender()
#     assert vtk_window._RenderWindow.GetStereoCapableWindow()
#     assert vtk_window._RenderWindow.GetAlphaBitPlanes()
#     assert vtk_window._RenderWindow.GetMultiSamples() == 0

# def test_VTK_foreground_render_settings(vtk_window):
#     assert vtk_window.foreground_renderer.GetLayer() == 1
#     assert vtk_window.foreground_renderer.GetUseDepthPeeling()
    
# def test_image_importer(vtk_window):
#     expected_extent = (0, 639, 0, 479, 0, 0)
    
#     assert vtk_window.image_importer.GetDataExtent() == expected_extent
#     assert vtk_window.image_importer.GetDataScalarTypeAsString() == "unsigned char"
#     assert vtk_window.image_importer.GetNumberOfScalarComponents() == 3
    
# def test_VTK_background_render_settings(vtk_window):
#     assert vtk_window.background_renderer.GetLayer() == 0
#     assert vtk_window.background_renderer.GetInteractive() == False

# def test_frame_pixels(vtk_window):
#     """Test pixel values in the first few frames to make sure
#      frames are being read correctly and that no frames are
#      skipped."""
    
#     frames_to_check = 10
    
#     for i in range(frames_to_check):
#         pixel = vtk_window.img[0,0,:]
#         expected_pixel = [i,i,i]
#         assert np.array_equal(pixel, expected_pixel)
#         vtk_window.update_background_renderer()

# def test_stereo_setting(vtk_window):
#     vtk_window.set_stereo_left()
#     assert vtk_window._RenderWindow.GetStereoTypeAsString() == "Left"

#     vtk_window.set_stereo_right()
#     assert vtk_window._RenderWindow.GetStereoTypeAsString() == "Right"
