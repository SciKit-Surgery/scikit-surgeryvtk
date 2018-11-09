import logging
import os
import json

import numpy as np
import vtk
from vtk.util import colors
from vtk.util.numpy_support import vtk_to_numpy

from PySide2.QtCore import Qt, QTimer, Signal, QEvent
from PySide2.QtWidgets import *

from sksurgeryoverlay.vtk.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

LOGGER = logging.getLogger(__name__)

class VTKOverlayWindow(QVTKRenderWindowInteractor):
    """Sets up a VTK Interactor Window that will be used to
     overlay VTK models on a video stream."""

    def __init__(self, frame_source, source_index):
        """
        Inputs:
        frame_source -  a SourceWrapper object (e.g. VideoSourceWrapper).
        source_index -  the frame source may contain frames from multiple
                        cameras/files. This specifies the index of the
                        source to use.
        """
        super().__init__()

        self.input = frame_source
        self.source_index = source_index
        self.save_overlaid_scene = False

        self.configure_render_window_for_stereo()
        self.configure_render_window_for_depth_peeling()

        # Two layers used, one for the background, one for the VTK overlay
        self._RenderWindow.SetNumberOfLayers(2)

        self.setup_foreground_renderer()

        self.setup_image_importer()
        self.setup_background_renderer()
        self.set_background_camera_to_fill_screen()

        if self.save_overlaid_scene:
            self.frames = []
            self.setup_numpy_exporter()

        self.screen = None
        self.screen_geometry = None
        self.timer = None

        self.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        self.Initialize()
        self.Start()

        self.show()

    def configure_render_window_for_stereo(self):
        """Enable VTK stereo settings for render window"""
        self._RenderWindow.StereoCapableWindowOn()
        self._RenderWindow.StereoRenderOn()

    def configure_render_window_for_depth_peeling(self):
        """Enable VTK Depth peeling settings for render window"""
        self._RenderWindow.AlphaBitPlanesOn()
        self._RenderWindow.SetMultiSamples(0)

    def setup_foreground_renderer(self):
        """Create and setup foreground renderer"""
        self.foreground_renderer = vtk.vtkRenderer()
        self.foreground_renderer.SetLayer(1)
        self.foreground_renderer.UseDepthPeelingOn()
        self.foreground_renderer.SetMaximumNumberOfPeels(100)
        self.foreground_renderer.SetOcclusionRatio(0.1)
        self._RenderWindow.AddRenderer(self.foreground_renderer)

    def setup_image_importer(self):
        """Set the parameters of the image importer, so that we
        get the correct image"""

        self.image_importer = vtk.vtkImageImport()

        self.background_shape = self.input.frames[self.source_index].shape
        self.update_image_importer_void_pointer()

        self.image_extent = (0, self.background_shape[1] - 1,
                             0, self.background_shape[0] - 1, 0, 0)
        self.image_importer.SetDataScalarTypeToUnsignedChar()
        self.image_importer.SetNumberOfScalarComponents(3)
        self.image_importer.SetWholeExtent(self.image_extent)
        self.image_importer.SetDataExtentToWholeExtent()

    def update_image_importer_void_pointer(self):
        """
        Set the void pointer for the image import filter, which should
        point to the image data being used for the background.
        If this isn't done, and the memory location of the frame changes,
        performance can become unstable.
        """
        self.flip_colour_space()
        self.image_importer.SetImportVoidPointer(self.rgb_frame.data)

    def flip_colour_space(self):
        """
        Change the colour space (RGB -> BGR, or BGR -> RGB)
        """
        self.rgb_frame = np.copy(self.input.frames[self.source_index][:,:,::-1]) 

    def setup_background_renderer(self):
        """Create and setup background renderer"""
        self.background_actor = vtk.vtkImageActor()
        self.background_actor.SetInputData(self.image_importer.GetOutput())
        self.background_renderer = vtk.vtkRenderer()
        self.background_renderer.SetLayer(0)
        self.background_renderer.InteractiveOff()
        self.background_renderer.AddActor(self.background_actor)
        self._RenderWindow.AddRenderer(self.background_renderer)

    def set_background_camera_to_fill_screen(self):
        """Position the background renderer camera, so that the image
        is maximised in the screen"""
        #pylint: disable=invalid-name

        origin = (0, 0, 0)
        spacing = (1, 1, 1)

        self.background_camera = self.background_renderer.GetActiveCamera()
        self.background_camera.ParallelProjectionOn()

        xc = origin[0] + 0.5 * (self.image_extent[0] +
                                self.image_extent[1]) * spacing[0]
        yc = origin[1] + 0.5 * (self.image_extent[2] +
                                self.image_extent[3]) * spacing[1]
        # xd = (self.image_extent[1] - self.image_extent[0] + 1) * spacing[0]
        yd = (self.image_extent[3] - self.image_extent[2] + 1) * spacing[1]
        d = self.background_camera.GetDistance()
        self.background_camera.SetParallelScale(0.5 * yd)
        self.background_camera.SetFocalPoint(xc, yc, 0.0)
        self.background_camera.SetPosition(xc, yc, -d)
        self.background_camera.SetViewUp(0.0, -1.0, 0.0)

    def get_pointer_to_background_image_data(self):
        """returns a memoryview of the background image data,
        which can be used as input to another viewer"""
        return self.img.data

    def setup_numpy_exporter(self):
        """
        Create a vtkWindowToImageFilter which will be used to convert
        vtk render data to a numpy array.
        """
        self.vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
        self.vtk_win_to_img_filter.SetInput(self._RenderWindow)

  
    def convert_scene_to_numpy_array(self):
        """
        Convert the current window view to a numpy array.
        """        
        
        self.vtk_win_to_img_filter.Modified()
        self.vtk_win_to_img_filter.Update()

        self.vtk_image = self.vtk_win_to_img_filter.GetOutput()
        width, height, _ = self.vtk_image.GetDimensions()
        self.vtk_array = self.vtk_image.GetPointData().GetScalars()
        components = self.vtk_array.GetNumberOfComponents()

        np_array =  vtk_to_numpy(self.vtk_array).reshape(height, width, components)

        # Create the output array on first iteration.
        # After that, just overwrite the existing one.
        if len(self.frames):
            self.frames[0] = np_array

        else:
            self.frames.append(np_array)


    def set_screen(self, screen):
        """Link the widget with a particular screen"""
        self.screen = screen

        self.move(screen.geometry().x(), screen.geometry().y())


    def add_VTK_models(self, models):
        """Add VTK models to the foreground"""
        for model in models:
            self.foreground_renderer.AddActor(model.actor)

        # Reset camera to centre on the loaded models
        self.foreground_renderer.ResetCamera()


    def update_background_renderer(self):
        """Update the background render with a new frame"""
        #pylint: disable=attribute-defined-outside-init

        # If the input has been updated, this will propagate through here
        # If it hasn't, nothing will change

        self.update_image_importer_void_pointer()
        self.image_importer.Modified()
        self.image_importer.Update()
        self._RenderWindow.Render()

        # We don't need to save the overlaid view at present.
        # Can be reenabled in future.
        if self.save_overlaid_scene:
            self.convert_scene_to_numpy_array()

    def start(self):
        """Set a timer running"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_background_renderer)
        self.timer.start(1000.0 / 40)

    def get_model_camera(self):
        """Return the camera that is looking at the VTK models"""
        return self.foreground_renderer.GetActiveCamera()

    def link_foreground_cameras(self, other_camera):
        """Set the foreground camera to track the view in another window"""
        self.foreground_renderer.SetActiveCamera(other_camera)

    def set_stereo_left(self):
        """ Set the render window to left stereo view"""
        self._RenderWindow.SetStereoTypeToLeft()

    def set_stereo_right(self):
        """ Set the render window to right stereo view"""
        self._RenderWindow.SetStereoTypeToRight()

    def get_camera_state(self):
        """Get all the necessary variables to allow the camera
        view to be restored"""
        #pylint: disable=unused-variable, eval-used
        camera = self.get_model_camera()
        camera_properties = {}

        properties_to_save = ["Position", "FocalPoint", "ViewUp", "ViewAngle",
                              "ParallelProjection", "ParallelScale",
                              "ClippingRange", "EyeAngle", "EyeSeparation",
                              "UseOffAxisProjection"]

        for camera_property in properties_to_save:

            # eval will run commands of the form
            # 'camera.GetPosition()', 'camera.GetFocalPoint()' for each property
            property_value = eval("camera.Get" + camera_property + "()")
            camera_properties[camera_property] = property_value

        return camera_properties

    def set_camera_state(self, camera_properties):
        """Set the camera properties to a particular view poisition/angle etc"""
        #pylint: disable=unused-variable, eval-used

        camera = self.get_model_camera()

        for camera_property, value in camera_properties.items():
            # eval statements 'camera.SetPosition(position)',
            # 'camera.SetFocalPoint(focalpoint) etc.
            eval("camera.Set" + camera_property + "(" + str(value) + ")")

    def stop_interactor(self):
        """Stop updating the window so that QApp
        can exit without errors"""
        self._RenderWindow.Finalize()
        self.TerminateApp()
