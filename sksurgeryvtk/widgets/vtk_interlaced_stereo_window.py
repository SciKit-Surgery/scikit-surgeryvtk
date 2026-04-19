# -*- coding: utf-8 -*-

"""
Module to provide an interlaced stereo window, designed for
driving things like the Storz 3D laparoscope monitor.
"""

# pylint: disable=c-extension-no-member, no-name-in-module, too-many-instance-attributes
import cv2
import numpy as np
from PySide6 import QtWidgets
import sksurgeryimage.processing.interlace as i
import sksurgeryvtk.widgets.vtk_base_stereo_window as bw
import sksurgeryvtk.widgets.vtk_overlay_window as ow


class VTKInterlacedStereoWindow(bw.VTKBaseStereoWindow):
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
                         yscale=1
                         )

        # This class adds an interlaced widget and a layout.
        self.interlaced_widget = ow.VTKOverlayWindow(
            offscreen=offscreen,
            init_widget=init_widget,
            aspect_ratio=aspect_ratio,
            xscale=1,
            yscale=1
        )
        self.interlaced_widget.setContentsMargins(0, 0, 0, 0)

        self.stacked = QtWidgets.QStackedWidget()
        self.stacked.addWidget(self.left_widget)
        self.stacked.addWidget(self.right_widget)
        self.stacked.addWidget(self.interlaced_widget)
        self.stacked.setContentsMargins(0, 0, 0, 0)
        self.stacked.setSizePolicy(self.size_policy)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.stacked)

        # Default the view to show the interlaced window.
        self.stacked.setCurrentIndex(2)

    # pylint: disable=invalid-name
    def paintEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        self.render()
        super().paintEvent(ev)

    # pylint: disable=invalid-name
    def resizeEvent(self, ev):
        """
        Ensure that the interlaced image is recomputed.
        """
        self.set_current_viewer_index(0)
        self.left_widget.resizeEvent(ev)
        self.left_widget.Render()
        self.left_widget.update()
        self.set_current_viewer_index(1)
        self.right_widget.resizeEvent(ev)
        self.right_widget.Render()
        self.right_widget.update()
        self.set_current_viewer_index(2)
        self.interlaced_widget.resizeEvent(ev)
        self.interlaced_widget.Render()
        self.interlaced_widget.update()
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

    def render(self):
        """
        Calls Render on all 3 contained vtk_overlay_windows.
        """
        self.left_widget.Render()
        self.left_widget.update()
        self.right_widget.Render()
        self.right_widget.update()

        left = self.left_widget.convert_scene_to_numpy_array()
        right = self.right_widget.convert_scene_to_numpy_array()

        left_rescaled = cv2.resize(left, (0, 0), fx=1.0, fy=0.5)
        right_rescaled = cv2.resize(right, (0, 0), fx=1.0, fy=0.5)

        if self.left_is_top:
            interlaced = i.interlace_to_new(left_rescaled,
                                            right_rescaled)
        else:
            interlaced = i.interlace_to_new(right_rescaled,
                                            left_rescaled)

        self.interlaced_widget.set_video_image(interlaced)
        self.interlaced_widget.Render()
        self.interlaced_widget.update()

    def save_scene_to_file(self, file_name):
        """
        Writes the interlaced widget contents to file.

        :param file_name: file name compatible with cv2.imwrite()
        """
        self.render()
        self.interlaced_widget.save_scene_to_file(file_name)
