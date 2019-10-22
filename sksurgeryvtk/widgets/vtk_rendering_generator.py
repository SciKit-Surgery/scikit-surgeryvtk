# -*- coding: utf-8 -*-

"""
Module to provide a basic VTK render window for test data generation.
"""

# pylint: disable=too-many-instance-attributes, no-name-in-module

import os
import numpy as np
import cv2
from PySide2 import QtWidgets
import sksurgerycore.utilities.file_utilities as fu
import sksurgerycore.configuration.configuration_manager as config
import sksurgeryvtk.widgets.vtk_overlay_window as vo
import sksurgeryvtk.models.surface_model_loader as sl
import sksurgeryvtk.camera.vtk_camera_model as cm
import sksurgeryvtk.utils.matrix_utils as mu


class VTKRenderingGenerator(QtWidgets.QWidget):
    """
    Class contains a VTKOverlayWindow and a few extra functions to
    facilitate rendering loops for generating test data.
    """
    def __init__(self,
                 models_file,
                 background_image,
                 intrinsic_file,
                 model_to_world=None,
                 camera_to_world=None,
                 left_to_right=None,
                 zbuffer=False,
                 sigma=0.0,
                 window_size=11
                 ):
        super().__init__()
        self.sigma = sigma
        self.window_size = window_size

        self.img = cv2.imread(background_image)

        self.intrinsics = np.loadtxt(intrinsic_file, dtype=np.float)

        self.configuration_manager = config.ConfigurationManager(models_file)
        self.configuration_data = self.configuration_manager.get_copy()

        file = fu.get_absolute_path_of_file(models_file)
        dirname = os.path.dirname(file)

        self.model_loader = sl.SurfaceModelLoader(self.configuration_data,
                                                  dirname
                                                  )

        self.overlay = vo.VTKOverlayWindow(zbuffer=zbuffer)
        self.overlay.set_video_image(self.img)
        self.overlay.add_vtk_models(self.model_loader.get_surface_models())

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.layout.addWidget(self.overlay)
        self.setLayout(self.layout)
        self.resize(self.img.shape[1], self.img.shape[0])

        self.model_to_world = np.eye(4)
        self.left_camera_to_world = np.eye(4)
        self.left_to_right = np.eye(4)
        self.camera_to_world = np.eye(4)
        self.setup_extrinsics(model_to_world,
                              camera_to_world,
                              left_to_right)

    def set_clipping_range(self, minimum, maximum):
        """
        Sets the clipping range on the foreground camera.
        :param minimum: minimum in millimetres
        :param maximum: maximum in millimetres
        """
        self.overlay.get_foreground_camera().SetClippingRange(minimum, maximum)

    def set_smoothing(self, sigma, window_size):
        """
        Sets the Gaussian blur.
        :param sigma: standard deviation of Gaussian function.
        :param window_size: sets the window size of Gaussian kernel (pixels).
        """
        self.sigma = sigma
        self.window_size = window_size

    def setup_extrinsics(self,
                         model_to_world,
                         camera_to_world,
                         left_to_right=None
                         ):
        """
        Decomposes parameter strings into 6DOF
        parameters, and sets up model-to-world and camera-to-world.

        :param model_to_world: list of rx,ry,rz,tx,ty,tz in degrees/millimetres
        :param camera_to_world: list of rx,ry,rz,tx,ty,tz in degrees/millimetres
        :param left_to_right: list of rx,ry,rz,tx,ty,tz in degrees/millimetres
        """
        if model_to_world is not None:
            self.model_to_world = mu.create_matrix_from_list(model_to_world)
            vtk_matrix = mu.create_vtk_matrix_from_numpy(self.model_to_world)
            for models in self.model_loader.get_surface_models():
                models.set_user_matrix(vtk_matrix)
        if camera_to_world is not None:
            self.left_camera_to_world = mu.create_matrix_from_list(
                camera_to_world)
        if left_to_right is not None:
            self.left_to_right = mu.create_matrix_from_list(left_to_right)
        self.camera_to_world = cm.compute_right_camera_pose(
            self.left_camera_to_world,
            self.left_to_right)
        self.overlay.set_camera_pose(self.camera_to_world)

    def get_image(self):
        """
        Returns the rendered image, with post processing like smoothing.
        :return: numpy ndarray representing rendered image (RGB)
        """
        self.overlay.Render()
        self.repaint()
        img = self.overlay.convert_scene_to_numpy_array()
        smoothed = img
        if self.sigma > 0:
            smoothed = cv2.GaussianBlur(img,
                                        (self.window_size, self.window_size),
                                        self.sigma)
        return smoothed
