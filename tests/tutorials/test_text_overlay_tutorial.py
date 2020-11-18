import sys
import cv2
from PySide2 import QtWidgets
from sksurgeryvtk.widgets import vtk_overlay_window
from sksurgeryvtk.text import text_overlay

def test_text():
    app = QtWidgets.QApplication([])

    background = cv2.imread('tests/data/rendering/background-960-x-540.png')
    overlay_window = vtk_overlay_window.VTKOverlayWindow()
    overlay_window.set_video_image(background)

    corner_annotation = text_overlay.VTKCornerAnnotation()
    corner_annotation.set_text(["1", "2", "3", "4"])
    overlay_window.add_vtk_actor(corner_annotation.text_actor, layer=2)

    large_text = text_overlay.VTKLargeTextCentreOfScreen("Central Text")
    large_text.set_colour(1.0, 0.0, 0.0)
    large_text.set_parent_window(overlay_window)
    overlay_window.add_vtk_actor(large_text.text_actor, layer=2)

    more_text = text_overlay.VTKText("More text", x=50, y=100)
    more_text.set_colour(0.0, 1.0, 0.0)
    overlay_window.add_vtk_actor(more_text.text_actor, layer=2)

    overlay_window.show()
    #sys.exit(app.exec_())


