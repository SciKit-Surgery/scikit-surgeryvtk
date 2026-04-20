# -*- coding: utf-8 -*-

"""
Module to provide an stacked stereo window, designed for
driving things like a 3D monitor that accepts left=top, right=bottom
"""

# pylint: disable=c-extension-no-member, no-name-in-module, too-many-instance-attributes
import cv2
import numpy as np
from PySide6 import QtWidgets
import sksurgeryvtk.widgets.vtk_base_stereo_window as bw


class VTKStackedStereoWindow(bw.VTKBaseStereoWindow):
    """
    Class to contain a pair of VTKOverlayWindows, left, right, that are
    stacked on top of each other. Left=top. Right=bottom.

    :param init_widget: If True we will call self.Initialize and self.Start
        as part of the init function. Set to false if you're on Linux.
    : param left_is_top: If True left is top. Else left is bottom.
    """
    # pylint: disable=too-many-positional-arguments
    def __init__(self,
                 offscreen=False,
                 left_camera_matrix=None,
                 right_camera_matrix=None,
                 clipping_range=(1, 10000),
                 init_widget=True,
                 left_is_top=True,
                 aspect_ratio=1
                 ):

        # Superclass creates left/right viewer.
        super().__init__(offscreen=offscreen,
                         left_camera_matrix=left_camera_matrix,
                         right_camera_matrix=right_camera_matrix,
                         clipping_range=clipping_range,
                         init_widget=init_widget,
                         left_is_top=left_is_top,
                         aspect_ratio=aspect_ratio,
                         xscale=1,
                         yscale=2
                         )

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        if self.left_is_top:
            self.layout.addWidget(self.left_widget)
            self.layout.addWidget(self.right_widget)
        else:
            self.layout.addWidget(self.right_widget)
            self.layout.addWidget(self.left_widget)

    def resizeEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        self.left_widget.resizeEvent(ev)
        self.left_widget.Render()
        self.left_widget.update()
        self.right_widget.resizeEvent(ev)
        self.right_widget.Render()
        self.right_widget.update()
        super().resizeEvent(ev)

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

        left_rescaled = cv2.resize(left_image, (0, 0), fx=1.0, fy=0.5)
        right_rescaled = cv2.resize(right_image, (0, 0), fx=1.0, fy=0.5)

        self.left_widget.set_video_image(left_rescaled)
        self.right_widget.set_video_image(right_rescaled)

    def render(self):
        """
        Simply triggers rendering on both widgets.
        """
        self.left_widget.Render()
        self.left_widget.update()
        self.right_widget.Render()
        self.right_widget.update()

    def save_scene_to_file(self, file_name):
        """
        Writes the interlaced widget contents to file.

        :param file_name: file name compatible with cv2.imwrite()
        """
        self.render()
        left_image = self.left_widget.convert_scene_to_numpy_array()
        right_image = self.right_widget.convert_scene_to_numpy_array()
        if self.left_is_top:
            stacked = np.vstack((left_image, right_image))
        else:
            stacked = np.vstack((right_image, left_image))
        cv2.imwrite(file_name, stacked)
