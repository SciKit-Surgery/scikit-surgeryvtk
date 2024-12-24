# -*- coding: utf-8 -*-

# pylint: disable=too-many-instance-attributes, no-name-in-module, too-many-statements
# pylint:disable=super-with-arguments, too-many-arguments, line-too-long, too-many-public-methods

"""
Module to provide a set of VTK renderers that can be used to create an Augmented Reality viewer.

Expected usage:

::

    window = VTKOverlayWindow()
    window.add_vtk_models(list)       # list of models. See class hierarchy in sksurgeryvtk/models.
    window.add_vtk_actor(actor)       # and/or individual VTK actor.
    window.set_camera_matrix(ndarray) # Set 3x3 ndarray of OpenCV camera intrinsic matrix.

    while True:

        image = # acquire np.ndarray image some how, e.g. from webcam or USB source.

        window.set_video_image(image)           # We use OpenCV, so this function expects BGR.
        window.set_camera_pose(camera_to_world) # set 4x4 ndarray representing camera pose.

"""

import logging

import cv2
import numpy as np
import sksurgerycore.utilities.validate_matrix as vm
import vtk
from PySide6.QtWidgets import QSizePolicy
from vtk.util.numpy_support import vtk_to_numpy
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import sksurgeryvtk.camera.vtk_camera_model as cm
import sksurgeryvtk.utils.matrix_utils as mu

LOGGER = logging.getLogger(__name__)


class VTKOverlayWindow(QVTKRenderWindowInteractor):
    """
    Sets up a VTK Overlay Window that can be used to
    overlay multiple VTK models on a video stream. Internally, the Window
    has 5 renderers, 0=backmost, 4=frontmost.

    # Layer 0: Video
    # Layer 1: VTK rendered models - e.g. internal anatomy
    # Layer 2: Video
    # Layer 3: VTK rendered models - e.g. external anatomy
    # Layer 4: VTK rendered text annotations.

    The video input should be BGR (like OpenCV provides). You can choose in the constructor
    whether the video should go to Layer 0 or Layer 2.

    If you put video in the Layer 0, and overlay models in Layer 1, you get a simple overlay
    which may be suitable for things like overlaying calibration points on chessboards,
    but you will get poor visual coherence for medical AR, as the bright colours of a synthetic overlay
    will always make the model appear in front of the video, even when you dial back the opacity of the model.

    If you put the video in Layer 2, it would obscure the rendered models in Layer 1.
    But you can apply a mask to the alpha channel setting the alpha to either 0 or 255.
    If the mask contains say a circle, it will have the effect of showing the video when the
    alpha channel is 255 and the rendering behind when the alpha channel is 0. So, you can
    use this to peek inside an organ by rendering the video in Layer 2 with a mask creating a hole,
    and the internal anatomy in Layer 1. Then you put the external anatomy, e.g. liver surface in Layer 3.

    :param offscreen: Enable/Disable offscreen rendering.
    :param camera_matrix: Camera intrinsics matrix.
    :param clipping_range: Near/Far clipping range.
    :param zbuffer: If True, will only render zbuffer of main renderer.
    :param opencv_style: If True, adopts OpenCV camera convention, otherwise OpenGL.
    :param init_pose: If True, will initialise the camera pose to identity.
    :param reset_camera: If True, resets camera when a new model is added.
    :param init_widget: If True we will call self.Initialize and self.Start
        as part of the init function. Set to false if you're on Linux.
    :param video_in_layer_0: If true, will add video to Layer 0, fully opaque, no masking.
    :param video_in_layer_2: If true, will add video to Layer 1. If layer_2_video_mask is present, will mask alpha channel.
    """

    def __init__(
        self,
        offscreen=False,
        camera_matrix=None,
        clipping_range=(1, 1000),
        zbuffer=False,
        opencv_style=True,
        init_pose=False,
        reset_camera=True,
        init_widget=True,
        video_in_layer_0=True,  # For backwards compatibility, prior to 3rd Feb 2024.
        video_in_layer_2=False,  # For backwards compatibility, prior to 3rd Feb 2024.
        layer_2_video_mask=None,  # For masking in Layer 3
        use_depth_peeling=True,  # Historically, has defaulted to true.
        layer_1_interactive=True, # For backwards compatibility, prior to 3rd Feb 2024.
        layer_3_interactive=False # For backwards compatibility, prior to 3rd Feb 2024.
    ):
        """
        Constructs a new VTKOverlayWindow.
        """
        super(VTKOverlayWindow, self).__init__()

        # Take and cache/store constructor arguments.
        if offscreen:
            self.GetRenderWindow().SetOffScreenRendering(1)
        else:
            self.GetRenderWindow().SetOffScreenRendering(0)
        self.camera_matrix = camera_matrix
        self.clipping_range = clipping_range
        self.zbuffer = zbuffer
        self.opencv_style = opencv_style
        self.reset_camera = reset_camera
        self.video_in_layer_0 = video_in_layer_0
        self.video_in_layer_2 = video_in_layer_2
        self.layer_2_video_mask = layer_2_video_mask

        # Some default reference data, or member variables.
        self.aspect_ratio = 1
        self.camera_to_world = np.eye(4)
        self.rgb_input = np.ones((400, 400, 3), dtype=np.uint8)
        self.rgb_frame = None
        self.rgba_frame = None
        self.screen = None
        self.mask_image = None

        # VTK objects initialised later
        self.output = None
        self.output_halved = None
        self.vtk_image = None
        self.vtk_array = None
        self.interactor = None

        # Setup an image importer to import the RGB video image.
        # Until the image is set, we use the default one created above.
        self.rgb_image_extent = (
            0,
            self.rgb_input.shape[1] - 1,
            0,
            self.rgb_input.shape[0] - 1,
            0,
            self.rgb_input.shape[2] - 1,
        )
        self.rgb_image_importer = vtk.vtkImageImport()
        self.rgb_image_importer.SetDataScalarTypeToUnsignedChar()
        self.rgb_image_importer.SetNumberOfScalarComponents(3)
        self.rgb_image_importer.SetDataExtent(self.rgb_image_extent)
        self.rgb_image_importer.SetWholeExtent(self.rgb_image_extent)

        # Setup an image importer to import the RGBA video image.
        # Until the image is set, we use the default one created above.
        self.rgba_image_extent = (
            0,
            self.rgb_input.shape[1] - 1,
            0,
            self.rgb_input.shape[0] - 1,
            0,
            self.rgb_input.shape[2],
        )
        self.rgba_image_importer = vtk.vtkImageImport()
        self.rgba_image_importer.SetDataScalarTypeToUnsignedChar()
        self.rgba_image_importer.SetNumberOfScalarComponents(4)
        self.rgba_image_importer.SetDataExtent(self.rgba_image_extent)
        self.rgba_image_importer.SetWholeExtent(self.rgba_image_extent)

        # Five layers used, see class level docstring.
        self.GetRenderWindow().SetNumberOfLayers(5)

        # Create and setup layer 0 (video) renderer.
        self.layer_0_image_actor = vtk.vtkImageActor()
        self.layer_0_image_actor.SetInputData(self.rgb_image_importer.GetOutput())
        self.layer_0_image_actor.VisibilityOff()
        self.layer_0_renderer = vtk.vtkRenderer()
        self.layer_0_renderer.SetLayer(0)
        self.layer_0_renderer.InteractiveOff()
        self.layer_0_renderer.AddActor(self.layer_0_image_actor)
        self.layer_0_camera = self.layer_0_renderer.GetActiveCamera()
        self.layer_0_camera.ParallelProjectionOn()

        # Create and setup layer 1 (VTK scene) renderer.
        self.layer_1_renderer = vtk.vtkRenderer()
        self.layer_1_renderer.SetLayer(1)
        self.layer_1_renderer.LightFollowCameraOn()
        if layer_1_interactive:
            self.layer_1_renderer.InteractiveOn()
        else:
            self.layer_1_renderer.InteractiveOff()

        # Create and setup layer 2 (masked video) renderer.
        self.layer_2_image_actor = vtk.vtkImageActor()
        self.layer_2_image_actor.SetInputData(self.rgba_image_importer.GetOutput())
        self.layer_2_image_actor.VisibilityOff()
        self.layer_2_renderer = vtk.vtkRenderer()
        self.layer_2_renderer.SetLayer(2)
        self.layer_2_renderer.InteractiveOff()
        self.layer_2_renderer.AddActor(self.layer_2_image_actor)
        self.layer_2_camera = self.layer_2_renderer.GetActiveCamera()
        self.layer_2_camera.ParallelProjectionOn()

        # Create and setup layer 3 (VTK scene) renderer.
        self.layer_3_renderer = vtk.vtkRenderer()
        self.layer_3_renderer.SetLayer(3)
        self.layer_3_renderer.LightFollowCameraOn()
        if layer_3_interactive:
            self.layer_3_renderer.InteractiveOn()
        else:
            self.layer_3_renderer.InteractiveOff()

        # Create and setup layer 4 (Overlay's, like text annotations) renderer.
        self.layer_4_renderer = vtk.vtkRenderer()
        self.layer_4_renderer.SetLayer(4)
        self.layer_4_renderer.LightFollowCameraOn()
        self.layer_4_renderer.InteractiveOff()

        # Enable VTK Depth peeling settings for render window, and renderers.
        if use_depth_peeling:
            self.GetRenderWindow().AlphaBitPlanesOn()
            self.GetRenderWindow().SetMultiSamples(0)
            self.layer_1_renderer.UseDepthPeelingOn()
            self.layer_1_renderer.SetMaximumNumberOfPeels(100)
            self.layer_1_renderer.SetOcclusionRatio(0.1)
            self.layer_3_renderer.UseDepthPeelingOn()
            self.layer_3_renderer.SetMaximumNumberOfPeels(100)
            self.layer_3_renderer.SetOcclusionRatio(0.1)

        # Use this to ensure the video is setup correctly at construction.
        self.set_video_image(self.rgb_input)

        # Setup the general interactor style. See VTK docs for alternatives.
        self.interactor = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.interactor)

        # Hook VTK world up to window
        # The ordering of these statements is important. If we want the
        # be able to move the camera around the foreground (or move the)
        # foreground objects using RenderWindowInteractor, the foreground
        # should be added last.
        if not self.zbuffer:
            self.GetRenderWindow().AddRenderer(self.layer_0_renderer)
            self.GetRenderWindow().AddRenderer(self.layer_1_renderer)
            self.GetRenderWindow().AddRenderer(self.layer_2_renderer)
            self.GetRenderWindow().AddRenderer(self.layer_3_renderer)
            self.GetRenderWindow().AddRenderer(self.layer_4_renderer)
        else:
            self.GetRenderWindow().AddRenderer(self.layer_1_renderer)

        # Set Qt Size Policy
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(self.size_policy)

        # Set default position to origin.
        if init_pose:
            default_pose = np.eye(4)
            self.set_camera_pose(default_pose)

        # Startup the widget
        if init_widget:
            self.Initialize()  # Allows the interactor to initialize itself.
            self.Start()  # Start the event loop.
        else:
            print(
                "\nYou've elected to initialize the VTKOverlayWindow(),",
                "be sure to do it in your calling function.",
            )

    def closeEvent(self, evt):
        super().closeEvent(evt)
        self.Finalize()

    def set_video_mask(self, mask_image):
        """
        Allows you to store a mask image, for alpha blending with layer 2 video channel.

        :param mask_image: numpy ndarray. Must be single channel, grey-scale, uint8, same size as input video.
        """
        if not isinstance(mask_image, np.ndarray):
            raise TypeError("Input is not an np.ndarray")
        if len(mask_image.shape) != 3:
            raise ValueError(
                "Input image should have X size, Y size and a single channel, e.g. grey scale."
            )
        if mask_image.shape[2] != 1:
            raise ValueError("Input image should be 1 channel, i.e. grey scale.")
        self.mask_image = mask_image

    def set_video_image(self, input_image):
        """
        Sets the video image that is used for the background.
        See also constructor args video_in_layer_0 and video_in_layer_2 which controls
        in which layer(s) the video image ends up.

        :param input_image: We use OpenCV, so the input image, should be BGR channel order.
        """
        if not isinstance(input_image, np.ndarray):
            raise TypeError("Input is not an np.ndarray")
        if len(input_image.shape) != 3:
            raise ValueError(
                "Input image should have X size, Y size and a number of channels, e.g. BGR."
            )
        if input_image.shape[2] != 3:
            raise ValueError("Input image should be 3 channel, i.e. BGR.")

        # Note: We will assume that any video comming in is 3 channel, BGR.
        # But layer 2 will use RGBA as we need the alpha channel.

        if (
            self.video_in_layer_0 and self.rgb_input.shape != input_image.shape
        ):  # i.e. if the size has changed.
            self.layer_0_image_actor.VisibilityOn()
            self.rgb_image_extent = (
                0,
                input_image.shape[1] - 1,
                0,
                input_image.shape[0] - 1,
                0,
                input_image.shape[2] - 1,
            )
            self.rgb_image_importer.SetDataExtent(self.rgb_image_extent)
            self.rgb_image_importer.SetWholeExtent(self.rgb_image_extent)

        if (
            self.video_in_layer_2 and self.rgb_input.shape != input_image.shape
        ):  # i.e. if the size has changed.
            self.layer_2_image_actor.VisibilityOn()
            self.rgba_image_extent = (
                0,
                input_image.shape[1] - 1,
                0,
                input_image.shape[0] - 1,
                0,
                input_image.shape[2],
            )
            self.rgba_image_importer.SetDataExtent(self.rgba_image_extent)
            self.rgba_image_importer.SetWholeExtent(self.rgba_image_extent)

        if self.video_in_layer_0 or self.video_in_layer_2:
            self.__update_video_image_cameras()
            self.__update_projection_matrices()

        if self.video_in_layer_0:
            self.rgb_input = input_image
            self.rgb_frame = np.copy(self.rgb_input[:, :, ::-1])
            self.rgb_image_importer.SetImportVoidPointer(self.rgb_frame.data)
            self.rgb_image_importer.SetDataExtent(self.rgb_image_extent)
            self.rgb_image_importer.SetWholeExtent(self.rgb_image_extent)
            self.rgb_image_importer.Modified()
            self.rgb_image_importer.Update()

        if self.video_in_layer_2:
            self.rgb_input = input_image
            self.rgba_frame = 255 * np.ones(
                (
                    input_image.shape[0],
                    input_image.shape[1],
                    input_image.shape[2] + 1,
                ),
                dtype=np.uint8,
            )
            self.rgba_frame[:, :, 0:3] = self.rgb_input[:, :, ::-1]
            if self.mask_image is not None:
                self.rgba_frame[:, :, 3:4] = self.mask_image
            self.rgba_image_importer.SetImportVoidPointer(self.rgba_frame.data)
            self.rgba_image_importer.SetDataExtent(self.rgba_image_extent)
            self.rgba_image_importer.SetWholeExtent(self.rgba_image_extent)
            self.rgba_image_importer.Modified()
            self.rgba_image_importer.Update()

    def __update_video_image_camera(self, camera, image_extent):
        """
        Internal method to position a renderers camera to face a video image,
        and to maximise the view of the image in the viewport.
        """
        origin = (0, 0, 0)
        spacing = (1, 1, 1)

        # Works out the number of millimetres to the centre of the image.
        x_c = origin[0] + 0.5 * (image_extent[0] + image_extent[1]) * spacing[0]
        y_c = origin[1] + 0.5 * (image_extent[2] + image_extent[3]) * spacing[1]

        # Works out the total size of the image in millimetres.
        i_w = (image_extent[1] - image_extent[0] + 1) * spacing[0]
        i_h = (image_extent[3] - image_extent[2] + 1) * spacing[1]

        # Works out the ratio of required size to actual size.
        w_r = i_w / self.width()
        h_r = i_h / self.height()

        # Then you adjust scale differently depending on whether the
        # screen is predominantly wider than your image, or taller.
        if w_r > h_r:
            scale = 0.5 * i_w * (self.height() / self.width())
        else:
            scale = 0.5 * i_h

        camera.SetFocalPoint(x_c, y_c, 0.0)
        camera.SetPosition(x_c, y_c, -1000)
        camera.SetViewUp(0.0, -1.0, 0.0)
        camera.SetClippingRange(990, 1010)
        camera.SetParallelProjection(True)
        camera.SetParallelScale(scale)

    def __update_video_image_cameras(self):
        """
        Position the background renderer camera, so that the video image
        is maximised and centralised in the screen.
        """
        if self.video_in_layer_0:
            self.__update_video_image_camera(
                self.layer_0_renderer.GetActiveCamera(), self.rgb_image_extent
            )
        if self.video_in_layer_2:
            self.__update_video_image_camera(
                self.layer_2_renderer.GetActiveCamera(), self.rgba_image_extent
            )

    def __update_projection_matrix(self, renderer, camera, input_image):
        """
        If a camera_matrix is available, then we are using a calibrated camera.
        This method recomputes the projection matrix, dependent on window size.
        """
        opengl_mat = None
        vtk_mat = None

        if self.camera_matrix is not None:
            if input_image is None:
                raise ValueError("Camera matrix is provided, but no image.")

            opengl_mat, vtk_mat = cm.set_camera_intrinsics(
                renderer,
                camera,
                input_image.shape[1],
                input_image.shape[0],
                self.camera_matrix[0][0],
                self.camera_matrix[1][1],
                self.camera_matrix[0][2],
                self.camera_matrix[1][2],
                self.clipping_range[0],
                self.clipping_range[1],
            )

            vpx, vpy, vpw, vph = cm.compute_scissor(
                self.width(),
                self.height(),
                input_image.shape[1],
                input_image.shape[0],
                self.aspect_ratio,
            )

            x_min, y_min, x_max, y_max = cm.compute_viewport(
                self.width(), self.height(), vpx, vpy, vpw, vph
            )

            renderer.SetViewport(x_min, y_min, x_max, y_max)

            vtk_rect = vtk.vtkRecti(vpx, vpy, vpw, vph)
            camera.SetUseScissor(True)
            camera.SetScissorRect(vtk_rect)

        return opengl_mat, vtk_mat

    def __update_projection_matrices(self):
        """
        If a camera_matrix is available, then we are using a calibrated camera.
        This method recomputes the projection matrix, dependent on window size.
        """
        renderer = self.get_foreground_renderer(layer=1)
        opengl_mat, vtk_mat = self.__update_projection_matrix(
            renderer,
            renderer.GetActiveCamera(),
            self.rgb_input,
        )

        renderer = self.get_foreground_renderer(layer=3)
        opengl_mat, vtk_mat = self.__update_projection_matrix(
            renderer,
            renderer.GetActiveCamera(),
            self.rgb_input,
        )

        return opengl_mat, vtk_mat

    def resizeEvent(self, ev):
        """
        Ensures that when the window is resized, the background renderer
        will correctly reposition the camera such that the image fully
        fills the screen, and if the foreground renderer is calibrated,
        also updates the projection matrix.

        :param ev: Event
        """
        super(VTKOverlayWindow, self).resizeEvent(ev)
        self.__update_video_image_cameras()
        self.__update_projection_matrices()
        self.Render()

    def set_camera_matrix(self, camera_matrix):
        """
        Sets the camera intrinsic matrix from a numpy 3x3 array.
        :param camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        """
        vm.validate_camera_matrix(camera_matrix)
        self.camera_matrix = camera_matrix
        opengl_mat, vtk_mat = self.__update_projection_matrices()
        self.Render()
        return opengl_mat, vtk_mat

    def set_camera_pose(self, camera_to_world):
        """
        Sets the camera position and orientation, from a numpy 4x4 array.
        :param camera_to_world: camera_to_world transform.
        """
        vm.validate_rigid_matrix(camera_to_world)
        self.camera_to_world = camera_to_world
        vtk_mat = mu.create_vtk_matrix_from_numpy(camera_to_world)
        cm.set_camera_pose(
            self.layer_1_renderer.GetActiveCamera(), vtk_mat, self.opencv_style
        )
        cm.set_camera_pose(
            self.layer_3_renderer.GetActiveCamera(), vtk_mat, self.opencv_style
        )
        self.Render()

    def add_vtk_models(self, models, layer=1):
        """
        Add VTK models to a renderer.
        Here, a 'VTK model' is any object that has an attribute called actor
        that is a vtkActor. See class hierarchy in sksurgeryvtk/models.

        :param models: list of VTK models.
        :param layer:  [1|3|4]. Render layer to add to, default 1.
        """
        renderer = self.get_foreground_renderer(layer=layer)

        for model in models:
            renderer.AddActor(model.actor)
            if model.get_outline():
                renderer.AddActor(model.get_outline_actor(renderer.GetActiveCamera()))

        if self.reset_camera:
            renderer.ResetCamera()

    def add_vtk_actor(self, actor, layer=1):
        """
        Add a vtkActor directly.

        :param actor: vtkActor
        :param layer: [1|3|4]. Render layer to add to, default 1.
        """
        renderer = self.get_foreground_renderer(layer=layer)

        renderer.AddActor(actor)

        if self.reset_camera:
            renderer.ResetCamera()

    def get_background_image_actor(self, layer=0):
        """
        Returns one of the background video image actors.

        :param layer: [0|2]. Index of image actor. Default 0.
        """
        if layer == 0:
            return self.layer_0_image_actor
        if layer == 1:
            raise ValueError("Layer 1 is not a background actor.")
        if layer == 2:
            return self.layer_2_image_actor
        if layer == 3:
            raise ValueError("Layer 3 is not a background actor.")
        if layer == 4:
            raise ValueError("Layer 4 is not a background actor.")

        raise ValueError("Didn't find background actor.")

    def get_background_renderer(self, layer=0):
        """
        Returns one of the background video layers.

        :param layer: [0|2]. Index of background image renderer. Default 0.
        """
        if layer == 0:
            return self.layer_0_renderer
        if layer == 1:
            raise ValueError("Layer 1 is not a background renderer.")
        if layer == 2:
            return self.layer_2_renderer
        if layer == 3:
            raise ValueError("Layer 3 is not a background renderer.")
        if layer == 4:
            raise ValueError("Layer 4 is not a background renderer.")

        raise ValueError("Didn't find background renderer.")

    def get_foreground_renderer(self, layer=1):
        """
        Returns the foreground vtkRenderer. For legacy compatibility,
        this will assume layer 1, like this class was pre-Feb 3rd 2024.

        :return: vtkRenderer
        """
        if layer == 0:
            raise ValueError("Layer 0 is not a foreground renderer.")
        if layer == 1:
            return self.layer_1_renderer
        if layer == 2:
            raise ValueError("Layer 2 is not a foreground renderer.")
        if layer == 3:
            return self.layer_3_renderer
        if layer == 4:
            return self.layer_4_renderer

        raise ValueError(f"Invalid layer specification:{layer}")

    def get_foreground_camera(self, layer=1):
        """
        Returns the camera for the foreground vtkRenderer. For legacy compatibility,
        this will assume layer 1, like this class was pre-Feb 3rd 2024.

        :returns: vtkCamera
        """
        renderer = self.get_foreground_renderer(layer)
        return renderer.GetActiveCamera()

    def set_foreground_camera(self, camera, layer=1):
        """
        Set the foreground camera to track the view in another window. For legacy compatibility,
        this will assume layer 1, like this class was pre-Feb 3rd 2024.
        """
        renderer = self.get_foreground_renderer(layer)
        renderer.SetActiveCamera(camera)

    def get_overlay_renderer(self):
        """
        This returns the top-most layer, where you might put text annotations for example.
        """
        return self.layer_4_renderer

    def set_screen(self, screen):
        """
        Link the widget with a particular screen.
        This is necessary when we have multi-monitor setups.

        :param screen: QScreen object.
        """
        self.screen = screen
        self.move(screen.geometry().x(), screen.geometry().y())

    def set_stereo_left(self):
        """
        Set the render window to left stereo view.
        """
        self._RenderWindow.SetStereoTypeToLeft()

    def set_stereo_right(self):
        """
        Set the render window to right stereo view.
        """
        self._RenderWindow.SetStereoTypeToRight()

    def convert_scene_to_numpy_array(self):
        """
        Convert the current window view to a numpy array.

        :return output: Scene as numpy array
        """
        vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
        vtk_win_to_img_filter.SetInput(self.GetRenderWindow())

        if not self.zbuffer:
            vtk_win_to_img_filter.SetInputBufferTypeToRGB()
            vtk_win_to_img_filter.Update()
            self.vtk_image = vtk_win_to_img_filter.GetOutput()
        else:
            vtk_win_to_img_filter.SetInputBufferTypeToZBuffer()
            vtk_scale = vtk.vtkImageShiftScale()
            vtk_scale.SetInputConnection(vtk_win_to_img_filter.GetOutputPort())
            vtk_scale.SetOutputScalarTypeToUnsignedChar()
            vtk_scale.SetShift(0)
            vtk_scale.SetScale(-255)
            vtk_scale.Update()
            self.vtk_image = vtk_scale.GetOutput()

        width, height, _ = self.vtk_image.GetDimensions()
        self.vtk_array = self.vtk_image.GetPointData().GetScalars()
        number_of_components = self.vtk_array.GetNumberOfComponents()

        np_array = vtk_to_numpy(self.vtk_array).reshape(
            height, width, number_of_components
        )
        self.output = cv2.flip(np_array, flipCode=0)
        return self.output

    def save_scene_to_file(self, file_name):
        """
        Save's the current screen to file.
        VTK works in RGB, but OpenCV assumes BGR, so swap the colour
        space before saving to file.
        :param file_name: must be compatible with cv2.imwrite()
        """
        self.convert_scene_to_numpy_array()
        self.output = cv2.cvtColor(self.output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_name, self.output)

    def get_camera_state(self, layer=1):
        """
        Get all the necessary variables to allow the camera
        view to be restored. For legacy compatibility,
        this will assume layer 1, like this class was pre-Feb 3rd 2024.
        """
        # pylint: disable=unused-variable, eval-used

        renderer = self.get_foreground_renderer(layer)
        camera = renderer.GetActiveCamera()
        camera_properties = {}

        properties_to_save = [
            "Position",
            "FocalPoint",
            "ViewUp",
            "ViewAngle",
            "ParallelProjection",
            "ParallelScale",
            "ClippingRange",
            "EyeAngle",
            "EyeSeparation",
            "UseOffAxisProjection",
        ]

        for camera_property in properties_to_save:
            # eval will run commands of the form
            # 'camera.GetPosition()', 'camera.GetFocalPoint()' for each property

            property_value = eval("camera.Get" + camera_property + "()")
            camera_properties[camera_property] = property_value

        return camera_properties

    def set_camera_state(self, camera_properties, layer=1):
        """
        Set the camera properties to a particular view poisition/angle etc. For legacy compatibility,
        this will assume layer 1, like this class was pre-Feb 3rd 2024.
        """
        # pylint: disable=unused-variable, eval-used

        renderer = self.get_foreground_renderer(layer)
        camera = renderer.GetActiveCamera()

        for camera_property, value in camera_properties.items():
            # eval statements 'camera.SetPosition(position)',
            # 'camera.SetFocalPoint(focalpoint) etc.
            eval("camera.Set" + camera_property + "(" + str(value) + ")")

    def remove_view_props_from_renderer(self, layer: int):
        """
        Method to remove all VTK actors from a single layer.
        """
        if layer == 0:
            self.layer_0_renderer.RemoveAllViewProps()
        elif layer == 1:
            self.layer_1_renderer.RemoveAllViewProps()
        elif layer == 2:
            self.layer_2_renderer.RemoveAllViewProps()
        elif layer == 3:
            self.layer_3_renderer.RemoveAllViewProps()
        elif layer == 4:
            self.layer_4_renderer.RemoveAllViewProps()
        else:
            raise ValueError(f"Layer={layer}, when it should be 0 <= layer <= 4.")

    def remove_all_models_from_renderer(self):
        """
        Convenience method to remove all models except background
        images, and text annotation overlays. i.e. just layers 1, 3.
        """
        self.remove_view_props_from_renderer(layer=1)
        self.remove_view_props_from_renderer(layer=3)
