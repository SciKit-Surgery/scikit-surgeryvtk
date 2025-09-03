# -*- coding: utf-8 -*-

# pylint: disable=too-many-instance-attributes, no-name-in-module, too-many-statements
# pylint:disable=super-with-arguments, too-many-arguments, line-too-long, too-many-public-methods

"""
Module to provide a single layer renderer, so that we can grab the
z-buffer using convert_scene_to_numpy_array().

Expected usage:

::

    window = VTKOverlayWindow()
    window.add_vtk_models(list)       # list of models. See class hierarchy in sksurgeryvtk/models.
    window.add_vtk_actor(actor)       # and/or individual VTK actor.
    window.set_camera_matrix(ndarray) # Set 3x3 ndarray of OpenCV camera intrinsic matrix.

    while True:

        image = # acquire np.ndarray image somehow, e.g. from webcam or USB source.

        window.set_video_image(image)           # We use OpenCV, so this function expects BGR.
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


class VTKZBufferWindow(bcw.VTKBaseCalibratedWindow):
    """
    Sets up a renderer that we can grab the z-buffer from.
    It's derived from VTKBaseCalibratedWindow so that the rendering of
    the model pose behaves in the same way as the base class and other
    derived classes. However, when you call anything to do with video images,
    they are ignored, as we don't want to include the image plane geometry in the
    z-buffer calculations. This class contains one renderer, as VTK
    seems to only extract the z-buffer properly if there is one renderer.

    You could say that the logic to control the camera could be refactored
    outside the base class, then this class could be separate, and not
    inherit from a base class it doesn't need. However, it's simple enough for now.

    :param offscreen: Enable/Disable offscreen rendering.
    :param camera_matrix: Camera intrinsics matrix.
    :param clipping_range: Near/Far clipping range.
    :param opencv_style: If True, adopts OpenCV camera convention, otherwise OpenGL.
    :param init_pose: If True, will initialise the camera pose to identity.
    :param reset_camera: If True, resets camera when a new model is added.
    :param init_widget: If True we call self.Initialise and self.Start
        as part of the init function. Set to false if you're on Linux.
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
        use_depth_peeling=True,
    ):
        """
        Constructs a new VTKZBufferWindow.
        """
        super(VTKZBufferWindow, self).__init__(offscreen,
                                               camera_matrix,
                                               clipping_range,
                                               opencv_style,
                                               reset_camera
                                               )
        LOGGER.info("Creating VTKZBufferWindow")

        # We don't ever render the image, but we store a ref
        # as we use it to compute camera parameters
        self.rgb_input = np.ones((400, 400, 3), dtype=np.uint8)

        # Create and setup layer 0 (video) renderer.
        self.renderer = vtk.vtkRenderer()

        # Enable VTK Depth peeling settings for render window, and renderers.
        if use_depth_peeling:
            self.GetRenderWindow().AlphaBitPlanesOn()
            self.GetRenderWindow().SetMultiSamples(0)
            self.renderer.UseDepthPeelingOn()
            self.renderer.SetMaximumNumberOfPeels(100)
            self.renderer.SetOcclusionRatio(0.1)

        # Set up the general interactor style. See VTK docs for alternatives.
        self.interactor = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.interactor)

        # Hook VTK world up to window
        self.GetRenderWindow().AddRenderer(self.renderer)

        # Set default position to origin.
        if init_pose:
            self._set_camera_to_origin()

        # Startup the widget
        self._startup_widget(init_widget)

        LOGGER.info("Created VTKZBufferWindow")

    def _update_video_image_cameras(self):
        """
        Not needed. Pass.
        """

    def _update_projection_matrices(self):
        """
        If a camera_matrix is available, then we are using a calibrated camera.
        This method recomputes the projection matrix, dependent on window size.
        """
        opengl_mat, vtk_mat = self._update_projection_matrix(
            self.renderer,
            self.renderer.GetActiveCamera(),
            self.rgb_input,
        )

        return opengl_mat, vtk_mat

    def _update_pose_matrices(self, matrix: np.ndarray):
        """
        Sets the pose on the camera. In this class there is only one.
        """
        cm.set_camera_pose(
            self.renderer.GetActiveCamera(), matrix, self.opencv_style
        )

    def get_renderer(self, layer=None):
        """
        Returns the only renderer in this class.
        """
        return self.renderer

    def remove_all_models(self):
        """
        Removes all models from the renderer.
        (useful if you are reloading data from disk etc.)
        """
        self.renderer.RemoveAllViewProps()

    def set_clipping_range(self, near: float, far: float):
        """
        Sets the clipping range on the single renderer/camera.
        """
        self.clipping_range = (near, far)
        self.renderer.GetActiveCamera().SetClippingRange(self.clipping_range)

    def convert_scene_to_numpy_array(self):
        """
        Main function to grab the z-buffer.
        """
        vtk_win_to_img_filter = vtk.vtkWindowToImageFilter()
        vtk_win_to_img_filter.SetInput(self.GetRenderWindow())
        vtk_win_to_img_filter.SetInputBufferTypeToZBuffer()
        vtk_win_to_img_filter.Update()

        stats_1 = vtk.vtkImageHistogramStatistics()
        stats_1.SetInputConnection(vtk_win_to_img_filter.GetOutputPort())
        stats_1.Update()

        min_1 = stats_1.GetMinimum()
        max_1 = stats_1.GetMaximum()

        scale_to_float = vtk.vtkImageShiftScale()
        scale_to_float.SetInputConnection(vtk_win_to_img_filter.GetOutputPort())
        scale_to_float.SetOutputScalarTypeToFloat()
        scale_to_float.SetShift(-min_1)
        scale_to_float.SetScale(255.0/(max_1 - min_1))
        scale_to_float.Update()

        scale_to_uchar = vtk.vtkImageShiftScale()
        scale_to_uchar.SetInputConnection(scale_to_float.GetOutputPort())
        scale_to_uchar.SetOutputScalarTypeToUnsignedChar()
        scale_to_uchar.SetShift(-255)
        scale_to_uchar.SetScale(-1)
        scale_to_uchar.Update()

        vtk_image = scale_to_uchar.GetOutput()

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
        Nothing to do. Pass.
        """

    def set_video_image(self, input_image: np.ndarray):
        """
        Stores the image, as it is used for calculating camera projection parameters.
        :param input_image: We use OpenCV, so the input image, should be BGR channel order.
        """
        self._validate_video_images(input_image)
        self.rgb_input = input_image
        self._update_projection_matrices()
