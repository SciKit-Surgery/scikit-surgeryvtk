# -*- coding: utf-8 -*-

# pylint: disable=too-many-instance-attributes, no-name-in-module, too-many-statements
# pylint:disable=too-many-positional-arguments, too-many-arguments, line-too-long, too-many-public-methods

"""
Module to provide a base class for OpenCV-style calibrated windows.
See also VTKOverlayWindow, VTKLegacyOverlayWindow and VTKZBufferWindow.
"""

import logging

import cv2
import numpy as np
import sksurgerycore.utilities.validate_matrix as vm
import vtk
from PySide6.QtWidgets import QSizePolicy
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sksurgeryvtk.models.vtk_base_model as bm
import sksurgeryvtk.camera.vtk_camera_model as cm
import sksurgeryvtk.utils.matrix_utils as mu

LOGGER = logging.getLogger(__name__)


class VTKBaseCalibratedWindow(QVTKRenderWindowInteractor):
    """
    Base class, providing common functions for derived classes.

    :param offscreen: Enable/Disable offscreen rendering.
    :param camera_matrix: Camera intrinsics matrix.
    :param clipping_range: Near/Far clipping range.
    :param opencv_style: If True, adopts OpenCV camera convention, otherwise OpenGL.
    :param reset_camera: If True, resets camera when a new model is added.
    """
    def __init__(
        self,
        offscreen=False,
        camera_matrix=None,
        clipping_range=(1, 1000),
        opencv_style=True,
        reset_camera=True
    ):
        """
        Constructs a new VTKBaseCalibratedWindow.
        """
        super().__init__()
        LOGGER.info("Creating VTKBaseCalibratedWindow")

        # Take and cache/store constructor arguments.
        if offscreen:
            self.GetRenderWindow().SetOffScreenRendering(1)
        else:
            self.GetRenderWindow().SetOffScreenRendering(0)
        self.camera_matrix = camera_matrix
        self.clipping_range = clipping_range
        self.opencv_style = opencv_style
        self.reset_camera = reset_camera

        # Member variables.
        self.aspect_ratio = 1
        self.camera_to_world = np.eye(4)
        self.screen = None

        # Set up the general interactor style. See VTK docs for alternatives.
        self.interactor = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.interactor)

        # Set Qt Size Policy
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(self.size_policy)

        LOGGER.info("Created VTKBaseCalibratedWindow")

    def closeEvent(self, evt):
        super().closeEvent(evt)
        self.Finalize()

    def resizeEvent(self, ev):
        """
        Ensures that when the window is resized, the derived classes
        will ensure that cameras are correctly scaled as the window size changes.
        :param ev: Event
        """
        super().resizeEvent(ev)
        self._update_video_image_cameras()
        self._update_projection_matrices()
        self.Render()

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
        self.GetRenderWindow().SetStereoTypeToLeft()

    def set_stereo_right(self):
        """
        Set the render window to right stereo view.
        """
        self.GetRenderWindow().SetStereoTypeToRight()

    def get_number_of_layers(self) -> int:
        """
        Returns the number of layers (i.e. vtkRenderers) registered with the vtkRenderWindow.
        """
        return self.GetRenderWindow().GetNumberOfLayers()

    def _set_camera_to_origin(self):
        """
        Internal method to reset the camera back to the origin.
        """
        default_pose = np.eye(4)
        self.set_camera_pose(default_pose)

    def _startup_widget(self, init_widget: bool):
        """
        Internal method to initialise the interactor, or log a warning if ignoring.
        """
        if init_widget:
            self.Initialize()  # Allows the interactor to initialize itself.
            self.Start()  # Start the event loop.
        else:
            print(
                "\nYou've elected to initialize the VTKBaseCalibratedWindow derived class(),",
                "be sure to do it in your calling function.",
            )

    def _validate_video_images(self, image: np.ndarray):
        """
        Internal method to do a few sanity checks on the image.
        """
        if not isinstance(image, np.ndarray):
            raise TypeError("Input is not an np.ndarray")
        if len(image.shape) != 3:
            raise ValueError(
                "Input image should have X size, Y size and a number of channels, e.g. BGR."
            )
        if image.shape[2] != 3:
            raise ValueError("Input image should be 3 channel, i.e. BGR.")

    def _validate_layer_number(self, layer: int):
        """
        Internal method to sanity check that the layer >=0 and < self.get_number_of_layers().
        """
        if layer is None or layer < 0 or layer >= self.get_number_of_layers():
            raise ValueError(f"layer should be >= 0 and < {self.get_number_of_layers()}, and it is {layer}.")

    def _update_video_image_camera(self, camera: vtk.vtkCamera, image_extent: [int]):
        """
        Internal method to position a renderers camera to face a video image,
        and to maximise the view of the image in the viewport.
        """
        # Issue #236: Take size from vtkRenderWindow, not Qt widget.
        # Issue #236: On Mac Retina displays, size given by Qt is halved.
        if self.width() == 0:
            LOGGER.warning("Qt window appears to have zero width, so abandoning _update_video_image_camera.")
            return
        if self.height() == 0:
            LOGGER.warning("Qt window appears to have zero height, so abandoning _update_video_image_camera.")
            return

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

    def _update_projection_matrix(self,
                                  renderer: vtk.vtkRenderer,
                                  camera: vtk.vtkCamera,
                                  input_image: np.ndarray):
        """
        If a camera_matrix is available, then we are using a calibrated camera.
        This method recomputes the projection matrix, dependent on window size.
        """
        opengl_mat = None
        vtk_mat = None

        # Issue #236: Take size from vtkRenderWindow, not Qt widget.
        # Issue #236: On Mac Retina displays, size given by Qt is halved.
        window_size = self.GetRenderWindow().GetSize()

        if window_size[0] == 0:
            LOGGER.warning("VTK Render Window appears to have zero width, so abandoning _update_projection_matrix.")
            return opengl_mat, vtk_mat
        if window_size[1] == 0:
            LOGGER.warning("VTK Render Window appears to have zero height, so abandoning _update_projection_matrix.")
            return opengl_mat, vtk_mat

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
                window_size[0],
                window_size[1],
                input_image.shape[1],
                input_image.shape[0],
                self.aspect_ratio,
            )

            x_min, y_min, x_max, y_max = cm.compute_viewport(
                window_size[0], window_size[1], vpx, vpy, vpw, vph
            )

            renderer.SetViewport(x_min, y_min, x_max, y_max)

            vtk_rect = vtk.vtkRecti(vpx, vpy, vpw, vph)
            camera.SetUseScissor(True)
            camera.SetScissorRect(vtk_rect)

        return opengl_mat, vtk_mat

    def _update_video_image_cameras(self):
        """
        Derived classes should implement, as they can decide what to do if they have
        single or multiple rendering cameras.
        """
        raise NotImplementedError("Derived classes should implement _update_video_image_cameras().")

    def _update_projection_matrices(self):
        """
        Derived classes should implement, as they can decide what to do if they have
        single or multiple rendering cameras.
        """
        raise NotImplementedError("Derived classes should implement _update_projection_matrices().")

    def _update_pose_matrices(self, matrix: np.ndarray):
        """
        Derived classes should implement, as they can decide what to do if they have
        single or multiple rendering cameras.
        """
        raise NotImplementedError("Derived classes should implement _update_pose_matrices().")

    def get_renderer(self, layer: int = None) -> vtk.vtkRenderer:
        """
        Derived classes should implement this, as it depends on how many
        renderers each derived class has.

        :param layer: an integer to indicate what layer.
        """
        raise NotImplementedError("Derived classes should implement get_renderer().")

    def remove_all_models(self):
        """
        Derived classes should implement this, as it depends on how many
        renderers each derived class has.
        """
        raise NotImplementedError("Derived classes should implement remove_all_models_from_renderer().")

    def set_clipping_range(self, near: float, far: float):
        """
        Derived classes should implement, as they may have multiple cameras to sort out.
        """
        raise NotImplementedError("Derived classes should implement set_clipping_range().")

    def convert_scene_to_numpy_array(self):
        """
        Convert the current window view to a numpy array.
        :return output: Scene as numpy array
        """
        raise NotImplementedError("Derived classes should implement set_clipping_range().")

    def get_camera(self, layer: int = None) -> vtk.vtkCamera:
        """
        Calls get_renderer(), and returns the corresponding vtkCamera.

        :param layer: an integer to indicate what layer.
        """
        renderer = self.get_renderer(layer=layer)
        return renderer.GetActiveCamera()

    def set_camera_matrix(self, camera_matrix: np.ndarray):
        """
        Sets the camera intrinsic matrix from a numpy 3x3 array.
        :param camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        """
        vm.validate_camera_matrix(camera_matrix)
        self.camera_matrix = camera_matrix
        opengl_mat, vtk_mat = self._update_projection_matrices()
        self.Render()
        return opengl_mat, vtk_mat

    def set_camera_pose(self, camera_to_world: np.ndarray):
        """
        Sets the camera position and orientation, from a numpy 4x4 array.
        :param camera_to_world: camera_to_world transform.
        """
        self.camera_to_world = camera_to_world
        vtk_mat = mu.create_vtk_matrix_from_numpy(camera_to_world)
        self._update_pose_matrices(vtk_mat)
        self.Render()

    def add_vtk_models(self, models: [bm.VTKBaseModel], layer: int = None):
        """
        Add VTK models to a renderer.
        Here, a 'VTK model' is any object that has an attribute called actor
        that is a vtkActor. See class hierarchy in sksurgeryvtk/models.

        :param models: list of VTK models.
        :param layer: passed to get_renderer().
        """
        renderer = self.get_renderer(layer=layer)

        for model in models:
            renderer.AddActor(model.actor)
            if model.get_outline():
                renderer.AddActor(model.get_outline_actor(renderer.GetActiveCamera()))

        if self.reset_camera:
            renderer.ResetCamera()

    def add_vtk_actor(self, actor: vtk.vtkActor, layer: int = None):
        """
        Add a vtkActor directly.

        :param actor: vtkActor
        :param layer: passed to get_renderer().
        """
        renderer = self.get_renderer(layer=layer)

        renderer.AddActor(actor)

        if self.reset_camera:
            renderer.ResetCamera()

    def save_scene_to_file(self, file_name: str):
        """
        Save's the current screen to file.
        VTK works in RGB, but OpenCV assumes BGR, so swap the colour
        space, if necessary, before saving to file.
        :param file_name: must be compatible with cv2.imwrite()
        """
        output = self.convert_scene_to_numpy_array()
        if len(output.shape) == 3:
            output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_name, output)
