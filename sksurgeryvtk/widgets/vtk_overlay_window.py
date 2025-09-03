# -*- coding: utf-8 -*-

# pylint:disable=too-many-instance-attributes, no-name-in-module, too-many-statements
# pylint:disable=super-with-arguments, too-many-arguments, line-too-long, too-many-public-methods

"""
Module to provide a 5-layer Augmented Reality renderer widget.

Expected usage:

::
    window = VTKOverlayWindow()
    window.add_vtk_models(list)       # list of models. See class hierarchy in sksurgeryvtk/models.
    window.add_vtk_actor(actor)       # and/or individual VTK actor.
    window.set_camera_matrix(ndarray) # Set 3x3 ndarray of OpenCV camera intrinsic matrix.

    while True:

        image = # acquire np.ndarray image somehow, e.g. from webcam or USB source.

        window.set_video_image(image)           # We use OpenCV, so this function expects BGR, undistorted image.
        window.set_camera_pose(camera_to_world) # set 4x4 ndarray representing camera pose.
"""

import logging
import numpy as np
import cv2
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import sksurgeryvtk.widgets.vtk_base_calibrated_window as bcw
import sksurgeryvtk.camera.vtk_camera_model as cm

LOGGER = logging.getLogger(__name__)


class VTKOverlayWindow(bcw.VTKBaseCalibratedWindow):
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
    whether the video should go to Layer 0 or Layer 2, or both.

    If you put video in the Layer 0, and overlay models in Layer 1, you get a simple overlay
    which may be suitable for things like overlaying calibration points on chessboards,
    but you will get poor visual coherence for medical AR, as the bright colours of a synthetic overlay
    will always make the model appear in front of the video, even when you dial back the opacity of the model.

    If you put the video in Layer 2, it would obscure the rendered models in Layer 1.
    But you can apply a mask to the alpha channel setting the alpha to between 0 and 255.
    If the mask contains say a circle, it will have the effect of showing the video when the
    alpha channel is 255 and the rendering behind when the alpha channel is 0. So, you can
    use this to peek inside an organ by rendering the video in Layer 2 with a mask creating a hole,
    and the internal anatomy in Layer 1. Then you put the external anatomy, e.g. liver surface in Layer 3.

    :param offscreen: Enable/Disable offscreen rendering.
    :param camera_matrix: Camera intrinsics matrix.
    :param clipping_range: Near/Far clipping range.
    :param opencv_style: If True, adopts OpenCV camera convention, otherwise OpenGL.
    :param init_pose: If True, will initialise the camera pose to identity.
    :param reset_camera: If True, resets camera when a new model is added.
    :param init_widget: If True we call self.Initialise and self.Start
        as part of the init function. Set to false if you're on Linux.
    :param video_in_layer_0: If true, will add video to Layer 0, fully opaque, no masking.
    :param video_in_layer_2: If true, will add video to Layer 1. If layer_2_video_mask is present, will mask alpha channel.
    :param layer_2_video_mask: Mask image for layer 2.
    :param layer_1_interactive: True if you want the VTK interactor to pickup events in this layer.
    :param layer_3_interactive: True if you want the VTK interactor to pickup events in this layer.
    layer_1_interactive and layer_3_interactive are mutually exclusive.
    """
    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        offscreen=False,
        camera_matrix=None,
        clipping_range=(1, 1000),
        opencv_style=True,
        init_pose=False,
        reset_camera=True,
        init_widget=True,
        video_in_layer_0=True,  # For backwards compatibility, prior to 3rd Feb 2024.
        video_in_layer_2=False,  # For backwards compatibility, prior to 3rd Feb 2024.
        layer_2_video_mask=None,  # For masking in Layer 3
        use_depth_peeling=True,
        layer_1_interactive=True,  # For backwards compatibility, prior to 3rd Feb 2024.
        layer_3_interactive=False  # For backwards compatibility, prior to 3rd Feb 2024.
    ):
        """
        Constructs a new VTKOverlayWindow.
        """
        super(VTKOverlayWindow, self).__init__(offscreen,
                                               camera_matrix,
                                               clipping_range,
                                               opencv_style,
                                               reset_camera
                                               )
        LOGGER.info("Creating VTKOverlayWindow")

        # Take and cache/store constructor arguments.
        self.video_in_layer_0 = video_in_layer_0
        self.video_in_layer_2 = video_in_layer_2
        self.layer_2_video_mask = layer_2_video_mask

        # Some default reference data, or member variables.
        self.rgb_input = np.ones((400, 400, 3), dtype=np.uint8)
        self.rgb_frame = None
        self.rgba_frame = None
        self.mask_image = None

        # Set up an image importer to import the RGB video image.
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

        # Set up an image importer to import the RGBA video image.
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
        self.layer_1_camera = self.layer_1_renderer.GetActiveCamera()
        self.layer_1_camera.SetClippingRange(self.clipping_range[0], self.clipping_range[1])

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
        self.layer_3_camera = self.layer_3_renderer.GetActiveCamera()
        self.layer_3_camera.SetClippingRange(self.clipping_range[0], self.clipping_range[1])

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

        # Hook VTK world up to window
        # The ordering of these statements is important. If we want the
        # be able to move the camera around the foreground (or move the)
        # foreground objects using RenderWindowInteractor, the foreground
        # should be added last.
        self.GetRenderWindow().AddRenderer(self.layer_0_renderer)
        self.GetRenderWindow().AddRenderer(self.layer_1_renderer)
        self.GetRenderWindow().AddRenderer(self.layer_2_renderer)
        self.GetRenderWindow().AddRenderer(self.layer_3_renderer)
        self.GetRenderWindow().AddRenderer(self.layer_4_renderer)

        # Set default position to origin.
        if init_pose:
            self._set_camera_to_origin()

        # Startup the widget
        self._startup_widget(init_widget)

        LOGGER.info("Created VTKOverlayWindow")

    def _remove_models_from_renderer(self, layer: int):
        """
        Method to remove all VTK actors from a single layer.
        """
        self._validate_layer_number(layer)
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

    def _update_video_image_cameras(self):
        """
        Position the background renderer camera, so that the video image
        is maximised and centralised in the screen.
        """
        self._update_video_image_camera(
            self.layer_0_renderer.GetActiveCamera(), self.rgb_image_extent
        )
        self._update_video_image_camera(
            self.layer_2_renderer.GetActiveCamera(), self.rgba_image_extent
        )

    def _update_projection_matrices(self):
        """
        If a camera_matrix is available, then we are using a calibrated camera.
        This method recomputes the projection matrix, dependent on window size.
        """
        for i in [1, 3]:
            renderer = self.get_renderer(layer=i)
            opengl_mat, vtk_mat = self._update_projection_matrix(
                renderer,
                renderer.GetActiveCamera(),
                self.rgb_input,
            )

        return opengl_mat, vtk_mat

    def _update_pose_matrices(self, matrix: np.ndarray):
        """
        Sets the pose on cameras in layer 1, 3.
        """
        for i in [1, 3]:
            renderer = self.get_renderer(layer=i)
            cm.set_camera_pose(
                renderer.GetActiveCamera(), matrix, self.opencv_style
            )

    def get_renderer(self, layer=None):
        """
        Returns a vtkRenderer. Overrides base class method.

        :param layer: if None, will default to 1.
        :return: vtkRenderer
        """
        if layer is None:
            layer = 1

        self._validate_layer_number(layer)

        if layer == 0:
            return self.layer_0_renderer
        if layer == 1:
            return self.layer_1_renderer
        if layer == 2:
            return self.layer_2_renderer
        if layer == 3:
            return self.layer_3_renderer
        if layer == 4:
            return self.layer_4_renderer
        raise ValueError(f"invalid layer={layer}")

    def remove_all_models(self):
        """
        Convenience method to remove all models except background
        images, and text annotation overlays. i.e. just layers 1, 3.
        """
        self._remove_models_from_renderer(layer=1)
        self._remove_models_from_renderer(layer=3)

    def set_clipping_range(self, near: float, far: float):
        """
        Sets the clipping range on the layers containing VTK models.
        """
        self.clipping_range = (near, far)
        for i in [1, 3]:
            renderer = self.get_renderer(layer=i)
            renderer.GetActiveCamera().SetClippingRange(self.clipping_range)

    def convert_scene_to_numpy_array(self):
        """
        Convert the current window view to a numpy array.

        :return output: Scene as numpy array
        """
        vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
        vtk_win_to_img_filter.SetInput(self.GetRenderWindow())

        vtk_win_to_img_filter.SetInputBufferTypeToRGB()
        vtk_win_to_img_filter.Update()
        vtk_image = vtk_win_to_img_filter.GetOutput()

        width, height, _ = vtk_image.GetDimensions()
        vtk_array = vtk_image.GetPointData().GetScalars()
        number_of_components = vtk_array.GetNumberOfComponents()

        np_array = vtk_to_numpy(vtk_array).reshape(
            height, width, number_of_components
        )
        output = cv2.flip(np_array, flipCode=0)
        return output

    def set_video_mask(self, mask_image: np.ndarray):
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

    def set_video_image(self, input_image: np.ndarray):
        """
        Sets the video image that is used for the background.

        See also constructor args video_in_layer_0 and video_in_layer_2 which controls
        in which layer(s) the video image ends up.

        :param input_image: We use OpenCV, so the input image, should be BGR channel order.
        """
        self._validate_video_images(input_image)

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

        if self.video_in_layer_0 or self.video_in_layer_2:
            self._update_video_image_cameras()
            self._update_projection_matrices()

    def get_background_image_actor(self, layer: int):
        """
        Returns one of the background video image actors.

        :param layer: [0|2]. Index of image actor. Default 0.
        """
        self._validate_layer_number(layer)
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

    def get_background_image_renderer(self, layer: int):
        """
        Returns one of the background video layers.

        :param layer: [0|2]. Index of background image renderer. Default 0.
        """
        self._validate_layer_number(layer)
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
