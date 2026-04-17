# -*- coding: utf-8 -*-

"""
Module to provide an interlaced stereo window, designed for
driving things like the Storz 3D laparoscope monitor.
"""

# pylint: disable=c-extension-no-member, no-name-in-module, too-many-instance-attributes

import copy
import cv2
import numpy as np
from PySide6 import QtWidgets
from PySide6.QtWidgets import QSizePolicy
import sksurgeryimage.processing.interlace as i
import sksurgeryvtk.widgets.vtk_overlay_window as ow


class VTKStereoInterlacedWindow(QtWidgets.QWidget):
    """
    Class to contain a pair of VTKOverlayWindows, left, right, that we render,
    grab, interlace, and then display as a background image
    on a separate VTKOverlayWindow.

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

        self.interlaced_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            init_widget=init_widget
        )
        self.interlaced_widget.setContentsMargins(0, 0, 0, 0)

        self.stacked = QtWidgets.QStackedWidget()
        self.stacked.addWidget(self.left_widget)
        self.stacked.addWidget(self.right_widget)
        self.stacked.addWidget(self.interlaced_widget)
        self.stacked.setContentsMargins(0, 0, 0, 0)

        # Set Qt Size Policy
        self.size_policy = \
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked.setSizePolicy(self.size_policy)
        self.setSizePolicy(self.size_policy)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.stacked)
        self.setContentsMargins(0, 0, 0, 0)

        self.left_camera_to_world = np.eye(4)
        self.right_camera_to_world = np.eye(4)

        # Default the view to show the interlaced window.
        self.stacked.setCurrentIndex(2)

    # pylint: disable=invalid-name
    def paintEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        super().paintEvent(ev)
        self.render()

    # pylint: disable=invalid-name
    def resizeEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        self.set_current_viewer_index(0)
        self.left_widget.resizeEvent(ev)
        self.left_widget.Render()
        self.left_widget.repaint()
        self.set_current_viewer_index(1)
        self.right_widget.resizeEvent(ev)
        self.right_widget.Render()
        self.right_widget.repaint()
        self.set_current_viewer_index(2)
        self.interlaced_widget.resizeEvent(ev)
        self.interlaced_widget.Render()
        self.interlaced_widget.repaint()
        super().resizeEvent(ev)


    def closeEvent(self, QCloseEvent):
        self.left_widget.Finalize()
        self.right_widget.Finalize()
        self.interlaced_widget.Finalize()
        super().closeEvent(QCloseEvent)

    def set_current_viewer_index(self, viewer_index):
        """
        Sets the current viewer selection.
        Defaults to 2

            0 = left
            1 = right
            2 = interlaced

        :param viewer_index: index of viewer, as above.
        """
        if viewer_index < 0:
            raise ValueError('viewer_index must be >= 0')
        if viewer_index > 2:
            raise ValueError('viewer_index must be <= 2')
        self.stacked.setCurrentIndex(viewer_index)

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
        self.left_camera_to_world = copy.deepcopy(left_camera_to_world)
        self.right_camera_to_world = copy.deepcopy(right_camera_to_world)

        self.left_widget.set_camera_pose(self.left_camera_to_world)
        self.right_widget.set_camera_pose(self.right_camera_to_world)

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
        self.left_widget.repaint()
        self.right_widget.Render()
        self.right_widget.repaint()

        left = self.left_widget.convert_scene_to_numpy_array()
        right = self.right_widget.convert_scene_to_numpy_array()

        cv2.imwrite('tests/output/matt_left.png', left)
        cv2.imwrite('tests/output/matt_right.png', right)

        left_rescaled = cv2.resize(left, (0, 0), fx=1, fy=0.5)
        right_rescaled = cv2.resize(right, (0, 0), fx=1, fy=0.5)

        cv2.imwrite('tests/output/matt_left_rescaled.png', left_rescaled)
        cv2.imwrite('tests/output/matt_right_rescaled.png', right_rescaled)

        interlaced = i.interlace_to_new(left_rescaled,
                                        right_rescaled)

        cv2.imwrite('tests/output/matt_interlaced.png', interlaced)

        self.interlaced_widget.set_video_image(interlaced)
        self.interlaced_widget.Render()
        self.interlaced_widget.repaint()

    def save_scene_to_file(self, file_name):
        """
        Writes the interlaced widget contents to file.

        :param file_name: file name compatible with cv2.imwrite()
        """
        self.render()
        self.interlaced_widget.save_scene_to_file(file_name)
