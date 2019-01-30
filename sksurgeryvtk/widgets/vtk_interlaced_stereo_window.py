# -*- coding: utf-8 -*-

"""
Module to provide an interlaced stereo window, designed for
driving things like the Storz 3D laparoscope monitor.
"""

from PySide2 import QtWidgets
from PySide2.QtWidgets import QSizePolicy
import sksurgeryvtk.widgets.vtk_overlay_window as ow
import logging

LOGGER = logging.getLogger(__name__)


class VTKStereoInterlacedWindow(QtWidgets.QWidget):
    """
    Class to contain a pair of VTKOverlayWindows, stacked with a QLabel widget
    containing the resulting interlaced picture.
    """
    def __init__(self, offscreen=False):
        super().__init__()
        self.left_widget = ow.VTKOverlayWindow(offscreen)
        self.right_widget = ow.VTKOverlayWindow(offscreen)
        self.interlaced_widget = QtWidgets.QLabel("Interlaced Picture Here")

        self.stacked = QtWidgets.QStackedWidget()
        self.stacked.addWidget(self.left_widget)
        self.stacked.addWidget(self.right_widget)
        self.stacked.addWidget(self.interlaced_widget)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.stacked)
        self.setLayout(self.layout)

        # Set Qt Size Policy
        self.size_policy = \
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

    def set_current_viewer_index(self, viewer_index):
        """
        Sets the current viewer selection.

            0 = left
            1 = right
            2 = interlaced

        :param viewer_index: index of viewer, as above.
        :return: Nothing
        """
        self.stacked.setCurrentIndex(viewer_index)

    def set_video_images(self, left_image, right_image):
        """
        Sets both left and right video images. Images
        must be the same shape.

        :param left_image: left numpy image
        :param right_image: right numpy image
        :return: nothing
        """
        self.left_widget.set_video_image(left_image)
        self.right_widget.set_video_image(right_image)
