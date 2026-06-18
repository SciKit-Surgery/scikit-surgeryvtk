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
                 init_widget=True,
                 left_is_top=True,
                 aspect_ratio=1,
                 xscale=1,
                 yscale=1
                 ):

        super().__init__()
        self.left_is_top = left_is_top
        self.xscale = xscale
        self.yscale = yscale
        self.aspect_ratio = aspect_ratio

        self.left_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            camera_matrix=left_camera_matrix,
            clipping_range=clipping_range,
            init_widget=init_widget,
            aspect_ratio=aspect_ratio,
            xscale=xscale,
            yscale=yscale
        )
        self.left_widget.setContentsMargins(0, 0, 0, 0)

        self.right_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            camera_matrix=right_camera_matrix,
            clipping_range=clipping_range,
            init_widget=init_widget,
            aspect_ratio=aspect_ratio,
            xscale=xscale,
            yscale=yscale
        )
        self.right_widget.setContentsMargins(0, 0, 0, 0)

        self.size_policy = \
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(self.size_policy)
        self.setContentsMargins(0, 0, 0, 0)

    def set_camera_matrices(self, left_camera_matrix, right_camera_matrix):
        """
        Sets both the left and right camera matrices (i.e. the intrinsics).

        :param left_camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        :param right_camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        """
        self.left_widget.set_camera_matrix(left_camera_matrix)
        self.right_widget.set_camera_matrix(right_camera_matrix)

    def set_camera_poses(self, left_camera_to_world, right_camera_to_world):
        """
        Sets the pose of both the left and right camera (i.e. the extrinsics).

        :param left_camera_to_world: 4x4 numpy ndarray, rigid transform
        :param right_camera_to_world: 4x4 numpy ndarray, rigid transform
        """
        self.left_widget.set_camera_pose(left_camera_to_world)
        self.right_widget.set_camera_pose(right_camera_to_world)

    def set_poses_from_left_camera(self, left_camera_to_world, left_to_right):
        """
        Sets the pose of both the left and right camera (i.e. the extrinsics).

        :param left_camera_to_world: 4x4 numpy ndarray, rigid transform
        :param left_to_right: 4x4 numpy ndarray, rigid transform
        """
        self.left_widget.set_camera_pose(left_camera_to_world)
        self.right_widget.set_camera_pose(np.linalg.inv(left_to_right @ np.linalg.inv(left_camera_to_world)))

    def set_poses_from_right_camera(self, right_camera_to_world, right_to_left):
        """
        Sets the pose of both the left and right camera (i.e. the extrinsics).

        :param right_camera_to_world: 4x4 numpy ndarray, rigid transform
        :param right_to_left: 4x4 numpy ndarray, rigid transform
        """
        self.left_widget.set_camera_pose(np.linalg.inv(right_to_left @ np.linalg.inv(right_camera_to_world)))
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
    def set_video_images(self, left_image, right_image):
        """
        Derived classes must implement this method.
        """

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
