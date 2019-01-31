# -*- coding: utf-8 -*-

"""
Module to provide a VTK scene on top of a video stream,
thereby enabling a basic augmented reality viewer.

Expected usage:

    window = VTKOverlayWindow()
    window.add_vtk_models(list) # list of VTK models
    window.add_vtk_actor(actor) # or individual actor

    while True:

        image = # acquire np.ndarray image some how
        window.set_video_image(image)
"""

# pylint: disable=too-many-instance-attributes, no-member, no-name-in-module

import logging
import numpy as np
import cv2
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PySide2.QtWidgets import QSizePolicy

from sksurgeryvtk.widgets.QVTKRenderWindowInteractor import \
    QVTKRenderWindowInteractor
import sksurgeryvtk.camera.vtk_camera_model as cm
import sksurgeryvtk.utils.projection_utils as pu

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
    def __init__(self,
                 offscreen=False,
                 camera_matrix=None,
                 clipping_range=(1, 10000),
                 aspect_ratio=1
                 ):
        """
        Constructs a new VTKOverlayWindow.
        """
        super(VTKOverlayWindow, self).__init__()

        if offscreen:
            self.GetRenderWindow().SetOffScreenRendering(1)
        else:
            self.GetRenderWindow().SetOffScreenRendering(0)

        self.camera_matrix = camera_matrix
        self.camera_to_world = np.eye(4)
        self.clipping_range = clipping_range
        self.aspect_ratio = aspect_ratio
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
        self.output_halved = None
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

        # Setup the general interactor style. See VTK docs for alternatives.
        self.interactor = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.interactor)

        # Hook VTK world up to window
        self.GetRenderWindow().AddRenderer(self.foreground_renderer)
        self.GetRenderWindow().AddRenderer(self.background_renderer)

        # Set Qt Size Policy
        self.size_policy = \
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
            self.__update_video_image_camera()

        self.input = input_image
        self.rgb_frame = np.copy(self.input[:, :, ::-1])
        self.image_importer.SetImportVoidPointer(self.rgb_frame.data)
        self.image_importer.SetDataExtent(self.image_extent)
        self.image_importer.SetWholeExtent(self.image_extent)
        self.image_importer.Modified()
        self.image_importer.Update()

    def __update_video_image_camera(self):
        """
        Position the background renderer camera, so that the video image
        is maximised and centralised in the screen.
        """
        self.background_camera = self.background_renderer.GetActiveCamera()

        origin = (0, 0, 0)
        spacing = (1, 1, 1)

        # Works out the number of millimetres to the centre of the image.
        x_c = origin[0] + 0.5 * (self.image_extent[0] +
                                 self.image_extent[1]) * spacing[0]
        y_c = origin[1] + 0.5 * (self.image_extent[2] +
                                 self.image_extent[3]) * spacing[1]

        # Works out the total size of the image in millimetres.
        i_w = (self.image_extent[1] - self.image_extent[0] + 1) * spacing[0]
        i_h = (self.image_extent[3] - self.image_extent[2] + 1) * spacing[1]

        # Works out the ratio of required size to actual size.
        w_r = i_w / self.width()
        h_r = i_h / self.height()

        # Then you adjust scale differently depending on whether the
        # screen is predominantly wider than your image, or taller.
        if w_r > h_r:
            scale = 0.5 * i_w * (self.height() / self.width())
        else:
            scale = 0.5 * i_h

        self.background_camera.SetFocalPoint(x_c, y_c, 0.0)
        self.background_camera.SetPosition(x_c, y_c, -1000)
        self.background_camera.SetViewUp(0.0, -1.0, 0.0)
        self.background_camera.SetClippingRange(990, 1010)
        self.background_camera.SetParallelProjection(True)
        self.background_camera.SetParallelScale(scale)

    def __update_projection_matrix(self):
        """
        If a camera_matrix is available, then we are using a calibrated camera.
        This method recomputes the projection matrix, dependent on window size.
        """
        if self.camera_matrix is not None:
            projection_matrix = cm.compute_projection_matrix(
                self.width(),
                self.height(),
                self.camera_matrix[0][0],
                self.camera_matrix[1][1],
                self.camera_matrix[0][2],
                self.camera_matrix[1][2],
                self.clipping_range[0],
                self.clipping_range[1],
                self.aspect_ratio
            )
            vtk_cam = self.get_foreground_camera()
            cm.set_projection_matrix(vtk_cam, projection_matrix)

    def resizeEvent(self, ev):
        """
        Ensures that when the window is resized, the background renderer
        will correctly reposition the camera such that the image fully
        fills the screen, and if the foreground renderer is calibrated,
        also updates the projection matrix.

        :param ev: Event
        """
        super(VTKOverlayWindow, self).resizeEvent(ev)
        self.__update_video_image_camera()
        self.__update_projection_matrix()

    def set_camera_matrix(self, camera_matrix):
        """
        Sets the camera projection matrix from a numpy 3x3 array.
        :param camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        """
        self.camera_matrix = camera_matrix
        self.__update_projection_matrix()

    def set_camera_pose(self, camera_to_world):
        """
        Sets the camera position and orientation, from a numpy 4x4 array.
        :param camera_to_world: camera_to_world transform.
        """
        self.camera_to_world = camera_to_world
        vtk_cam = self.get_foreground_camera()
        vtk_mat = cm.create_vtk_matrix_from_numpy(camera_to_world)
        cm.set_camera_pose(vtk_cam, vtk_mat)

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

    def set_stereo_left(self):
        """ Set the render window to left stereo view"""
        self._RenderWindow.SetStereoTypeToLeft()

    def set_stereo_right(self):
        """ Set the render window to right stereo view"""
        self._RenderWindow.SetStereoTypeToRight()

    def convert_scene_to_numpy_array(self):
        """
        Convert the current window view to a numpy array.
        """
        # Used to output the on-screen image.
        self.vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
        self.vtk_win_to_img_filter.SetInput(self.GetRenderWindow())
        self.vtk_win_to_img_filter.SetScale(1, 1)
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

        # At the moment, this seems to be twice as big as I'd expect.
        # Don't know why yet. More investigation needed.
        self.output_halved = cv2.resize(self.output, (0, 0),
                                        fx=0.5, fy=0.5,
                                        interpolation=cv2.INTER_NEAREST)

        # For now, outputting twice as big image, helps with interlacing.
        return self.output

    def save_scene_to_file(self, file_name):
        """
        Save's the current screen to file.

        :param file_name: compatible with cv2.imwrite()
        """
        self.convert_scene_to_numpy_array()
        cv2.imwrite(file_name, self.output_halved)  # Work around, see above.

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

    def project_points(self, world_points, normals=None):
        """
        Projects the 3D world points, by the current transformation.
        If you are not using a calibrated camera, will use a slow loop.
        If you are, it will do them in a bulk operation using OpenCV.
        If you provide normals, will only project points that face camera.

        :param world_points: nx3 numpy ndarray representing 3D points.
        :param normals: nx3 numpy ndarray representing normals for said points.
        :return: pixel locations of projected 3D points
        """
        world_to_camera = np.linalg.inv(self.camera_to_world)

        if self.camera_matrix is None:
            if normals is not None:
                raise ValueError('Not implemented yet, please help out')
            else:
                projected = np.zeros((world_points[0], 2))
                coord_3d = vtk.vtkCoordinate()
                coord_3d.SetCoordinateSystemToWorld()
                counter = 0
                for w_p in world_points:
                    coord_3d.SetValue(w_p[0], w_p[1], w_p[2])
                    p_x, p_y = coord_3d.GetComputedDisplayValue(
                        self.foreground_renderer)
                    p_y = self.height() - 1 - p_y
                    projected[counter][0] = p_x
                    projected[counter][1] = p_y
                    counter += 1
        else:
            if normals is not None:
                projected = pu.project_facing_points(world_points,
                                                     normals,
                                                     world_to_camera,
                                                     self.camera_matrix
                                                     )
            else:
                projected = pu.project_points(world_points,
                                              world_to_camera,
                                              self.camera_matrix
                                              )
        return projected
