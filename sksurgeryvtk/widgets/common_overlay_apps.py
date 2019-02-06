"""Common use cases for vtk_overlay_window"""

#pylint: disable=no-member, no-name-in-module, protected-access
# coding=utf-8
import cv2

from PySide2.QtCore import QTimer
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from sksurgeryvtk.models.vtk_surface_model_directory_loader \
    import VTKSurfaceModelDirectoryLoader

class OverlayBaseApp():
    """
    Base class for applications that use vtk_overlay_window.
    The update() method should be implemented in the child
    class.

    :param video_source: OpenCV compatible video source (int or filename)
    """
    def __init__(self, video_source):
        self.vtk_overlay_window = VTKOverlayWindow()
        self.video_source = cv2.VideoCapture(video_source)
        self.update_rate = 30
        self.img = None
        self.timer = None

    def start(self):
        """Show the overlay widget and
        set a timer running"""
        self.vtk_overlay_window.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000.0 / self.update_rate)

    def add_vtk_models_from_dir(self, directory):
        """
        Add VTK models to the foreground.
        :param: directory, location of models
        """
        model_loader = VTKSurfaceModelDirectoryLoader(directory)
        self.vtk_overlay_window.add_vtk_models(model_loader.models)

    def update(self):
        """ Update the scene background and/or foreground.
            Should be implemented by sub class """

        raise NotImplementedError('Should have implemented this method.')

    def stop(self):
        """
        Make sure that the VTK Interactor terminates nicely, otherwise
        it can throw some error messages, depending on the usage.
        """
        self.vtk_overlay_window._RenderWindow.Finalize()
        self.vtk_overlay_window.TerminateApp()

class OverlayOnVideoFeed(OverlayBaseApp):
    """
    Uses the acquired video feed as the background image,
    with no additional processing.
    """
    def update(self):
        _, self.img = self.video_source.read()
        self.vtk_overlay_window.set_video_image(self.img)
        self.vtk_overlay_window._RenderWindow.Render()
