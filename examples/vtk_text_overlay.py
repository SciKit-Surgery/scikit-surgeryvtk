# coding=utf-8

import logging
import sys

from PySide2.QtWidgets import QApplication, QInputDialog

from sksurgeryvtk.widgets import vtk_overlay_window, common_overlay_apps
from sksurgeryvtk.text import text_overlay
from sksurgeryvtk.models import vtk_base_model

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class TextOverlayDemo(common_overlay_apps.OverlayOnVideoFeed):

    def __init__(self, video_source):

        super().__init__(video_source)
        # Set the vtk window title
        self.vtk_overlay_window.GetRenderWindow().SetWindowName("Click on image to add text")
        
        # Add annotations to each corner
        corner_annotation = text_overlay.VTKCornerAnnotation()
        self.vtk_overlay_window.add_vtk_actor(corner_annotation.text_actor)

        # Add a listener for left mouse clicks
        self.vtk_overlay_window.AddObserver('LeftButtonPressEvent',self.mouse_click_callback)

    def mouse_click_callback(self, obj, ev):
        """ Callback to create text at left mouse click position. """

        # Open a dialog box to get the input text
        text, ret = QInputDialog.getText(None, "Create text overlay", "Text:")

        # Get the mouse click position
        x, y = obj.GetEventPosition()
        
        # Create a text actor and add it to the VTK scene
        vtk_text = text_overlay.VTKText(text, x, y)
        vtk_text.set_parent_window(self.vtk_overlay_window)
        self.vtk_overlay_window.add_vtk_actor(vtk_text.text_actor)

def main():

    app = QApplication([])

    video_source = 0
    demo = TextOverlayDemo(video_source)
    demo.start()

    return sys.exit(app.exec_())

if __name__ == "__main__":
    main()