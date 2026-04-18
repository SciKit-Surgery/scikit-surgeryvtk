# -*- coding: utf-8 -*-

"""
Base class for vtk_interlaced_stereo_window.py and vtk_stacked_stereo_window.py
"""

import abc
import numpy as np
from PySide6 import QtWidgets
from PySide6.QtWidgets import QSizePolicy
import sksurgeryvtk.widgets.vtk_overlay_window as ow


class VTKBaseStereoWindow(QtWidgets.QWidget):
    """
    Class to contain a pair of VTKOverlayWindows, left, right,
    and common methods.

    :param init_widget: If True we will call self.Initialize and self.Start
        as part of the init function. Set to false if you're on Linux.
    """
    # pylint: disable=too-many-positional-arguments
    def __init__(self,
                 offscreen=False,
                 left_camera_matrix=None,
                 right_camera_matrix=None,
                 clipping_range=(1, 10000),
                 init_widget=True
                 ):

        super().__init__()
        self.left_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            camera_matrix=left_camera_matrix,
            clipping_range=clipping_range,
            init_widget=init_widget
        )
        self.left_widget.setContentsMargins(0, 0, 0, 0)

        self.right_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            camera_matrix=right_camera_matrix,
            clipping_range=clipping_range,
            init_widget=init_widget
        )
        self.right_widget.setContentsMargins(0, 0, 0, 0)

        self.size_policy = \
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(self.size_policy)
        self.setContentsMargins(0, 0, 0, 0)

    def set_video_images(self, left_image, right_image):
        """
        Sets both left and right video images. Images
        must be the same shape, and have an even number of rows.

        :param left_image: left numpy image
        :param right_image: right numpy image
        :raises: ValueError, TypeError
        """
        if not isinstance(left_image, np.ndarray):
            raise TypeError('left image is not an np.ndarray')
        if not isinstance(right_image, np.ndarray):
            raise TypeError('right image is not an np.ndarray')
        if left_image.shape != right_image.shape:
            raise ValueError('left and right images differ in shape')
        if left_image.shape[0] % 2 != 0:
            raise ValueError('left image does not have an even number of rows')
        if right_image.shape[0] % 2 != 0:
            raise ValueError('right image does not have an even number of rows')

        self.left_widget.set_video_image(left_image)
        self.right_widget.set_video_image(right_image)

    def set_camera_matrices(self, left_camera_matrix, right_camera_matrix):
        """
        Sets both the left and right camera matrices.

        :param left_camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        :param right_camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        """
        self.left_widget.set_camera_matrix(left_camera_matrix)
        self.right_widget.set_camera_matrix(right_camera_matrix)

    def set_camera_poses(self, left_camera_to_world, right_camera_to_world):
        """
        Sets the pose of both the left and right camera.

        :param left_camera_to_world: 4x4 numpy ndarray, rigid transform
        :param right_camera_to_world: 4x4 numpy ndarray, rigid transform
        """
        self.left_widget.set_camera_pose(left_camera_to_world)
        self.right_widget.set_camera_pose(right_camera_to_world)

    def add_vtk_models(self, models):
        """
        Add models to both left and right widgets.
        Here a model is anything with an attribute called actor that
        is a vtkActor.

        :param models: vtk_base_model
        """
        self.left_widget.add_vtk_models(models)
        self.right_widget.add_vtk_models(models)

    def add_vtk_actor(self, actor):
        """
        Adds a vtkActor to both left and right widgets.

        :param actor: vtkActor
        """
        self.left_widget.add_vtk_actor(actor)
        self.right_widget.add_vtk_actor(actor)

    @abc.abstractmethod
    def render(self):
        """
        Derived classes must implement this method.
        """

    @abc.abstractmethod
    def save_scene_to_file(self, file_name):
        """
        Derived classes must implement this method.
        """
