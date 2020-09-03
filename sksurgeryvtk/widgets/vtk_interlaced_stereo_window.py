# -*- coding: utf-8 -*-

"""
Module to provide an interlaced stereo window, designed for
driving things like the Storz 3D laparoscope monitor.
"""

# pylint: disable=c-extension-no-member, no-name-in-module, too-many-instance-attributes
#pylint:disable=super-with-arguments

import cv2
import numpy as np
from PySide2 import QtWidgets
from PySide2.QtWidgets import QSizePolicy
import sksurgeryimage.processing.interlace as i
import sksurgerycore.utilities.validate_matrix as vm
import sksurgeryvtk.widgets.vtk_overlay_window as ow
import sksurgeryvtk.camera.vtk_camera_model as cm


class VTKStereoInterlacedWindow(QtWidgets.QWidget):
    """
    Class to contain a pair of VTKOverlayWindows, stacked with a QLabel widget
    containing the resulting interlaced picture.
    """
    def __init__(self,
                 offscreen=False,
                 left_camera_matrix=None,
                 right_camera_matrix=None,
                 clipping_range=(1, 10000)
                 ):

        super().__init__()
        self.left_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            camera_matrix=left_camera_matrix,
            clipping_range=clipping_range
            )

        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.right_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            camera_matrix=right_camera_matrix,
            clipping_range=clipping_range
            )

        self.right_widget.setContentsMargins(0, 0, 0, 0)

        self.left_rescaled = None
        self.right_rescaled = None

        self.interlaced_widget = ow.VTKOverlayWindow(
            offscreen=offscreen
            )

        self.interlaced_widget.setContentsMargins(0, 0, 0, 0)

        self.stacked_stereo_widget = ow.VTKOverlayWindow(
            offscreen=offscreen
            )
        self.stacked_stereo_widget.setContentsMargins(0, 0, 0, 0)

        self.stacked = QtWidgets.QStackedWidget()
        self.stacked.addWidget(self.left_widget)
        self.stacked.addWidget(self.right_widget)
        self.stacked.addWidget(self.interlaced_widget)
        self.stacked.addWidget(self.stacked_stereo_widget)
        self.stacked.setContentsMargins(0, 0, 0, 0)

        # Set Qt Size Policy
        self.size_policy = \
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked.setSizePolicy(self.size_policy)
        self.setSizePolicy(self.size_policy)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.stacked)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)

        self.interlaced = np.eye(1)
        self.interlaced_swapped = np.eye(1)
        self.left_camera_to_world = np.eye(4)
        self.left_to_right = np.eye(4)

        self.default_viewer_index = 3
        self.stacked.setCurrentIndex(self.default_viewer_index)

    # pylint: disable=invalid-name
    def paintEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        super(VTKStereoInterlacedWindow, self).paintEvent(ev)
        self.render()

    # pylint: disable=invalid-name
    def resizeEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        super(VTKStereoInterlacedWindow, self).resizeEvent(ev)
        self.render()

    def set_current_viewer_index(self, viewer_index):
        """
        Sets the current viewer selection.
        Defaults to self.default_viewer_ndex.

            0 = left
            1 = right
            2 = interlaced
            3 = stacked

        :param viewer_index: index of viewer, as above.
        """
        self.stacked.setCurrentIndex(viewer_index)

    def set_view_to_interlaced(self):
        """ Sets the current view to interlaced. """
        self.set_current_viewer_index(2)

    def set_view_to_stacked(self):
        """ Sets the current view to stacked. """
        self.set_current_viewer_index(3)

    def set_video_images(self, left_image, right_image):
        """
        Sets both left and right video images. Images
        must be the same shape, and have an even number of rows.

        :param left_image: left numpy image
        :param right_image: right numpy image
        :raises ValueError, TypeError
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
        self.__update_left_right()
        self.__update_interlaced()
        self.__update_stacked()

    def __update_left_right(self):
        """
        Update and grab current scene from left and right widgets.
        """

        left = self.left_widget.convert_scene_to_numpy_array()
        right = self.right_widget.convert_scene_to_numpy_array()

        self.left_rescaled = cv2.resize(left, (0, 0), fx=1, fy=0.5)
        self.right_rescaled = cv2.resize(right, (0, 0), fx=1, fy=0.5)

    def __update_interlaced(self):
        """
        Updates the interlaced image by forcing a repaint on left and right,
        grabbing the current scene from those widgets, interlacing it and
        placing it as the background on the interlaced widget.
        """
        self.interlaced = i.interlace_to_new(self.left_rescaled,
                                             self.right_rescaled)

        self.interlaced_widget.set_video_image(self.interlaced)

    def __update_stacked(self):
        """
        Updates the stacked image by forcing a repaint on left and right,
        grabbing the current scene from those widgets, stacking it and
        placing it as the background on the stacked_stereo widget.
        """
        stacked_image = i.stack_to_new(self.left_rescaled, self.right_rescaled)
        self.stacked_stereo_widget.set_video_image(stacked_image)

    def set_camera_matrices(self, left_camera_matrix, right_camera_matrix):
        """
        Sets both the left and right camera matrices.

        :param left_camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        :param right_camera_matrix: numpy 3x3 ndarray containing fx, fy, cx, cy
        """
        self.left_widget.set_camera_matrix(left_camera_matrix)
        self.right_widget.set_camera_matrix(right_camera_matrix)

    def set_left_to_right(self, left_to_right):
        """
        Sets the left_to_right transform (stereo extrinsics).

        :param left_to_right: 4x4 numpy ndarray, rigid transform
        """
        vm.validate_rigid_matrix(left_to_right)
        self.left_to_right = left_to_right

    def set_camera_poses(self, left_camera_to_world):
        """
        Sets the pose of both the left and right camera.
        If you haven't set the left_to_right transform, it will be identity.

        :param left_camera_to_world: 4x4 numpy ndarray, rigid transform
        """
        self.left_camera_to_world = left_camera_to_world
        right_camera_to_world = cm.compute_right_camera_pose(
            self.left_camera_to_world, self.left_to_right)

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

    def render(self):
        """
        Calls Render on all 3 contained vtk_overlay_windows.
        """
        self.left_widget.Render()
        self.right_widget.Render()
        self.__update_interlaced()
        self.interlaced_widget.Render()
        self.__update_stacked()
        self.stacked_stereo_widget.Render()

        self.stacked.repaint()

    def save_scene_to_file(self, file_name):
        """
        Writes the currently displayed widget contents to file.

        :param file_name: file name compatible with cv2.imwrite()
        """
        self.render()

        self.stacked.currentWidget().save_scene_to_file(file_name)
