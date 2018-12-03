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
        
        # Add annotations to each corner
        corner_annotation = vtk_text.VTKCornerAnnotation()
        self.vtk_window.foreground_renderer.AddActor(corner_annotation.text_actor)

        # Add a listener for left mouse clicks
        self.vtk_window.AddObserver('LeftButtonPressEvent',self.mouse_click_callback)

        self.text_overlays = []


    def run(self):

        while True:
            self.wrapper.get_next_frames()
            cv2.waitKey(1)
            self.vtk_window.update_background_renderer() 


    def mouse_click_callback(self, obj, ev):
        """ Callback to create text at left mouse click position. """

        text, ret = QInputDialog.getText(None, "Create text overlay", "Text:")
        x, y = obj.GetEventPosition()
        
        
        # Create a text actor and add it to the VTK scene
        text_overlay = vtk_text.VTKText(text, x, y)
        self.text_overlays.append(text_overlay)

        # Store the window size, to allow for correct positioning of text
        # if window is resized.
        screen_size_x, screen_size_y = self.vtk_window.GetRenderWindow().GetSize()
        text_overlay.calculate_relative_position_in_window(screen_size_x, screen_size_y)

        self.vtk_window.foreground_renderer.AddActor(text_overlay.text_actor)

        # Add a listener for window resize events
        self.vtk_window.AddObserver('ModifiedEvent', self.window_resize_callback)

    def window_resize_callback(self, obj, ev):
        """ Callback to update the text location when the window is resized.
        """

        screen_size_x, screen_size_y = self.vtk_window.GetRenderWindow().GetSize()
        for overlay in self.text_overlays:
            overlay.set_relative_position_in_window(screen_size_x, screen_size_y)    

def main():

    app = QApplication([])

    demo = TextOverlayDemo()
    demo.run()

if __name__ == "__main__":
    main()