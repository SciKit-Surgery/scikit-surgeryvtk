# -*- coding: utf-8 -*-

"""
Module to provide an interlaced stereo window, designed for
driving things like the Storz 3D laparoscope monitor.
"""

# pylint: disable=c-extension-no-member, no-member, no-name-in-module

import cv2
import numpy as np
from PySide2 import QtWidgets
from PySide2.QtWidgets import QSizePolicy
import sksurgeryimage.processing.interlace as i
import sksurgeryvtk.widgets.vtk_overlay_window as ow


class VTKStereoInterlacedWindow(QtWidgets.QWidget):
    """
    Class to contain a pair of VTKOverlayWindows, stacked with a QLabel widget
    containing the resulting interlaced picture.
    """
    def __init__(self, offscreen=False):
        super().__init__()
        self.left_widget = ow.VTKOverlayWindow(offscreen)
        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.right_widget = ow.VTKOverlayWindow(offscreen)
        self.right_widget.setContentsMargins(0, 0, 0, 0)
        self.interlaced_widget = ow.VTKOverlayWindow(offscreen)
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

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.stacked)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)

        self.interlaced = np.eye(1)

    # pylint: disable=invalid-name
    def resizeEvent(self, ev):
        """
        Ensures that when the window is resized, the interlaced image is
        recomputed.
        """
        super(VTKStereoInterlacedWindow, self).resizeEvent(ev)
        self.__update_interlaced()

    def set_current_viewer_index(self, viewer_index):
        """
        Sets the current viewer selection.

            0 = left
            1 = right
            2 = interlaced

        :param viewer_index: index of viewer, as above.
        """
        self.stacked.setCurrentIndex(viewer_index)

    def set_video_images(self, left_image, right_image):
        """
        Sets both left and right video images. Images
        must be the same shape, and have an even number of rows.

        :param left_image: left numpy image
        :param right_image: right numpy image
        :raises ValueError
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
        self.__update_interlaced()

    def __update_interlaced(self):
        """
        Updates the interlaced image by forcing a repaint on left and right,
        grabbing the current scene from those widgets, interlacing it and
        placing it as the background on the interlaced widget.
        """
        if self.interlaced_widget.isHidden():
            return
        self.left_widget.repaint()
        self.right_widget.repaint()
        left = self.left_widget.convert_scene_to_numpy_array()
        left_rescaled = cv2.resize(left, (0, 0), fx=1, fy=0.5)
        left_flipped = cv2.flip(left_rescaled, flipCode=0)
        right = self.right_widget.convert_scene_to_numpy_array()
        right_rescaled = cv2.resize(right, (0, 0), fx=1, fy=0.5)
        right_flipped = cv2.flip(right_rescaled, flipCode=0)
        self.interlaced = i.interlace_to_new(left_flipped, right_flipped)
        self.interlaced_widget.set_video_image(self.interlaced)
