#Add current dir to path, to discover sksurgeryoverlay package
# Needs to be run from scikit-surgeryoverlay directory
import os, sys
sys.path.append(os.getcwd())

import logging
import cv2

from PySide2.QtWidgets import QApplication, QInputDialog

# sksurgeyimage should be pip installed
from sksurgeryimage.acquire import source_wrapper
from sksurgeryoverlay.vtk import vtk_overlay_window, vtk_model, vtk_text

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class TextOverlayDemo:

    def __init__(self):

        self.wrapper = source_wrapper.VideoSourceWrapper()

        cam_source = 0
        self.wrapper.add_camera(cam_source)
        self.vtk_window = vtk_overlay_window.VTKOverlayWindow(self.wrapper.sources[0])

        # Set the vtk window title
        self.vtk_window.GetRenderWindow().SetWindowName("Click on image to add text")

        # Add annotations to each corner
        corner_annotation = vtk_text.VTKCornerAnnotation()
        self.vtk_window.foreground_renderer.AddActor(corner_annotation.text_actor)

        # Add a listener for left mouse clicks
        self.vtk_window.AddObserver('LeftButtonPressEvent',self.mouse_click_callback)

    def run(self):

        while True:
            self.wrapper.get_next_frames()
            cv2.waitKey(1)
            self.vtk_window.update_background_renderer() 


    def mouse_click_callback(self, obj, ev):
        """ Callback to create text at left mouse click position. """

        # Open a dialog box to get the input text
        text, ret = QInputDialog.getText(None, "Create text overlay", "Text:")

        # Get the mouse click position
        x, y = obj.GetEventPosition()
        
        # Create a text actor and add it to the VTK scene
        text_overlay = vtk_text.VTKText(text, x, y)
        text_overlay.set_parent_window(self.vtk_window)
        self.vtk_window.foreground_renderer.AddActor(text_overlay.text_actor)

def main():

    app = QApplication([])

    demo = TextOverlayDemo()
    demo.run()

if __name__ == "__main__":
    main()