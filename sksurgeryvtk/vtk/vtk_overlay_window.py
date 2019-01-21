# -*- coding: utf-8 -*-

"""
Module to provide a VTK scene on top of a video stream,
thereby enabling a basic augmented reality viewer.

Expected usage:

    window = VTKOverlayWindow()
    window.add_vtk_models(list) # list of VTK models
    window.add_vtk_actor(actor)

    while True:

        image = # acquire np.ndarray image some how
        window.set_video_image(image)
"""

# pylint: disable=too-many-instance-attributes, no-member, no-name-in-module

import logging
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QSizePolicy

from sksurgeryvtk.vtk.QVTKRenderWindowInteractor import \
    QVTKRenderWindowInteractor

LOGGER = logging.getLogger(__name__)

class VTKOverlayWindow(QVTKRenderWindowInteractor):
    """
    Sets up a VTK Overlay Window that can be used to
    overlay multiple VTK models on a video stream. Internally, the Window
    has 2 renderers. The background renderer displays
    the video image in the background. The foreground renderer
    displays a VTK scene overlaid on the background. If you make your
    VTK models semi-transparent you get a merging effect.
    """
    def __init__(self, offscreen=False):
        """
        Constructs a new VTKOverlayWindow.
        """
        super(VTKOverlayWindow, self).__init__()

        if offscreen:
            self.GetRenderWindow().SetOffScreenRendering(1)
        else:
            self.GetRenderWindow().SetOffScreenRendering(0)

        self.input = np.ones((400, 400, 3), dtype=np.uint8)
        self.rgb_frame = None
        self.screen = None

        # VTK objects initialised later
        self.foreground_renderer = None
        self.image_importer = None
        self.background_shape = None
        self.image_importer = None
        self.image_extent = None
        self.background_actor = None
        self.background_renderer = None
        self.background_camera = None
        self.output = None
        self.vtk_win_to_img_filter = None
        self.vtk_image = None
        self.vtk_array = None
        self.interactor = None

        # Enable VTK Depth peeling settings for render window.
        self.GetRenderWindow().AlphaBitPlanesOn()
        self.GetRenderWindow().SetMultiSamples(0)

        # Two layers used, one for the background, one for the VTK overlay
        self.GetRenderWindow().SetNumberOfLayers(2)

        # Create and setup foreground (VTK scene) renderer.
        self.foreground_renderer = vtk.vtkRenderer()
        self.foreground_renderer.SetLayer(1)
        self.foreground_renderer.UseDepthPeelingOn()
        self.foreground_renderer.SetMaximumNumberOfPeels(100)
        self.foreground_renderer.SetOcclusionRatio(0.1)

        # Use an image importer to import the video image.
        self.background_shape = self.input.shape
        self.image_extent = (0, self.background_shape[1] - 1,
                             0, self.background_shape[0] - 1, 0, 0)
        self.image_importer = vtk.vtkImageImport()
        self.image_importer.SetDataScalarTypeToUnsignedChar()
        self.image_importer.SetNumberOfScalarComponents(3)
        self.image_importer.SetDataExtent(self.image_extent)
        self.image_importer.SetWholeExtent(self.image_extent)

        self.set_video_image(self.input)

        # Create and setup background (video) renderer.
        self.background_actor = vtk.vtkImageActor()
        self.background_actor.SetInputData(self.image_importer.GetOutput())
        self.background_renderer = vtk.vtkRenderer()
        self.background_renderer.SetLayer(0)
        self.background_renderer.InteractiveOff()
        self.background_renderer.AddActor(self.background_actor)
        self.background_camera = self.background_renderer.GetActiveCamera()
        self.background_camera.ParallelProjectionOn()

        # Used to output the on-screen image.
        self.vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
        self.vtk_win_to_img_filter.SetScale(1, 1)
        self.vtk_win_to_img_filter.SetInput(self.GetRenderWindow())
        self.vtk_image = self.vtk_win_to_img_filter.GetOutput()
        self.vtk_array = self.vtk_image.GetPointData().GetScalars()

        # Setup the general interactor style. See VTK docs for alternatives.
        self.interactor = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.interactor)

        # Hook VTK world up to window
        self.GetRenderWindow().AddRenderer(self.foreground_renderer)
        self.GetRenderWindow().AddRenderer(self.background_renderer)

        # Set Qt Size Policy
        self.size_policy = \
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

        # Startup the widget fully
        self.Initialize()
        self.Start()

    def set_video_image(self, input_image):
        """
        Set the video image that is used for the background.
        """
        if not isinstance(input_image, np.ndarray):
            raise TypeError('Input is not an np.ndarray')

        if self.input.shape != input_image.shape:
            self.background_shape = input_image.shape
            self.image_extent = (0, self.background_shape[1] - 1,
                                 0, self.background_shape[0] - 1, 0, 0)
            self.image_importer.SetDataExtent(self.image_extent)
            self.image_importer.SetWholeExtent(self.image_extent)
            self.update_video_image_camera()

        self.input = input_image
        self.rgb_frame = np.copy(self.input[:, :, ::-1])
        self.image_importer.SetImportVoidPointer(self.rgb_frame.data)
        self.image_importer.SetDataExtent(self.image_extent)
        self.image_importer.SetWholeExtent(self.image_extent)
        self.image_importer.Modified()
        self.image_importer.Update()

    def update_video_image_camera(self):
        """
        Position the background renderer camera, so that the video image
        is maximised in the screen. Once the screen is initialised,
        only really needed when the image is changed.
        """
        origin = (0, 0, 0)
        spacing = (1, 1, 1)

        self.background_camera = self.background_renderer.GetActiveCamera()

        x_c = origin[0] + 0.5 * (self.image_extent[0] +
                                 self.image_extent[1]) * spacing[0]
        y_c = origin[1] + 0.5 * (self.image_extent[2] +
                                 self.image_extent[3]) * spacing[1]
        # x_d = (self.image_extent[1] - self.image_extent[0] + 1) * spacing[0]
        y_d = (self.image_extent[3] - self.image_extent[2] + 1) * spacing[1]
        distance = self.background_camera.GetDistance()
        self.background_camera.SetParallelScale(0.5 * y_d)
        self.background_camera.SetFocalPoint(x_c, y_c, 0.0)
        self.background_camera.SetPosition(x_c, y_c, -distance)
        self.background_camera.SetViewUp(0.0, -1.0, 0.0)

    def add_vtk_models(self, models):
        """
        Add VTK models to the foreground renderer.
        Here, a 'VTK model' is any object that has an actor attribute
        that is a vtkActor.

        :param models: list of VTK models.
        """
        for model in models:
            self.foreground_renderer.AddActor(model.actor)

        # Reset camera to centre on the loaded models
        self.foreground_renderer.ResetCamera()

    def add_vtk_actor(self, actor):
        """
        Add a vtkActor directly.

        :param actor: vtkActor
        """
        self.foreground_renderer.AddActor(actor)
        self.foreground_renderer.ResetCamera()

    def get_foreground_renderer(self):
        """
        Returns the foreground vtkRenderer.

        :return: vtkRenderer
        """
        return self.foreground_renderer

    def get_foreground_camera(self):
        """
        Returns the camera for the foreground renderer.

        :returns: vtkCamera
        """
        return self.foreground_renderer.GetActiveCamera()

    def set_foreground_camera(self, camera):
        """
        Set the foreground camera to track the view in another window.
        """
        self.foreground_renderer.SetActiveCamera(camera)

    def set_screen(self, screen):
        """
        Link the widget with a particular screen.
        This is necessary when we have multi-monitor setups.

        :param screen: QScreen object.
        """
        self.screen = screen
        self.move(screen.geometry().x(), screen.geometry().y())

    def heightForWidth(self, width):
        #pylint: disable=invalid-name
        """
        Override Qt heightForWidth function, used to maintain aspect
        ratio of widget.
        This will only be active is the widget is placed inside a QLayout.
        If you don't want this auto scaling,
        set self.size_policy.setHeightForWidth(False)
        """

        aspect_ratio = self.background_shape[0] / self.background_shape[1]
        return width * aspect_ratio

    def sizeHint(self):
        """
        Override Qt sizeHint.
        """

        return QSize(self.background_shape[1], self.background_shape[0])

    def convert_scene_to_numpy_array(self):
        """
        Convert the current window view to a numpy array.
        """
        self.vtk_win_to_img_filter.Modified()
        self.vtk_win_to_img_filter.Update()

        self.vtk_image = self.vtk_win_to_img_filter.GetOutput()
        width, height, _ = self.vtk_image.GetDimensions()
        self.vtk_array = self.vtk_image.GetPointData().GetScalars()
        number_of_components = self.vtk_array.GetNumberOfComponents()

        np_array = vtk_to_numpy(self.vtk_array).reshape(height,
                                                        width,
                                                        number_of_components)
        self.output = np_array
        return self.output

    def get_camera_state(self):
        """
        Get all the necessary variables to allow the camera
        view to be restored.
        """
        # pylint: disable=unused-variable, eval-used

        camera = self.get_foreground_camera()
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
        """
        Set the camera properties to a particular view poisition/angle etc.
        """
        # pylint: disable=unused-variable, eval-used

        camera = self.get_foreground_camera()

        for camera_property, value in camera_properties.items():
            # eval statements 'camera.SetPosition(position)',
            # 'camera.SetFocalPoint(focalpoint) etc.
            eval("camera.Set" + camera_property + "(" + str(value) + ")")
