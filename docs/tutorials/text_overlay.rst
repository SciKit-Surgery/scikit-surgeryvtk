Add Text to VTKOverlayWindow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Classes are provided that can add persistent text to a VTKOverlayWindow as:

* Corner annotations
* Large centered text
* Generic text anywhere in the window

.. image:: text_overlay.png

First, we need to import relevant modules, setup a Qt Application, and create a VTKOverlayWindow.

.. code-block:: python

    import cv2
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
    from sksurgeryvtk.widgets import vtk_overlay_window
    from sksurgeryvtk.text import text_overlay

    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
	    app = QApplication([])
    else:
	    app = QApplication.instance()

    window_qwidget = QWidget()
    window_qwidget.show()
    layout = QVBoxLayout()
    window_qwidget.setLayout(layout)

    background = cv2.imread('tests/data/rendering/background-960-x-540.png')
    overlay_window = vtk_overlay_window.VTKOverlayWindow(offscreen=False, init_widget=False)
    overlay_window.set_video_image(background)

    layout.addWidget(overlay_window)
    overlay_window.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())


We can now create a corner annotations:

.. code-block:: python

    corner_annotation = text_overlay.VTKCornerAnnotation()
    corner_annotation.set_text(["1", "2", "3", "4"])
    overlay_window.add_vtk_actor(corner_annotation.text_actor, layer=2)

centred text:

.. code-block:: python

    large_text = text_overlay.VTKLargeTextCentreOfScreen("Central Text")
    large_text.set_colour(1.0, 0.0, 0.0)
    large_text.set_parent_window(overlay_window)
    overlay_window.add_vtk_actor(large_text.text_actor, layer=2)

and place some text at given co-ordinates in the window:

.. code-block:: python

    more_text = text_overlay.VTKText("More text", x=50, y=100)
    more_text.set_colour(0.0, 1.0, 0.0)
    overlay_window.add_vtk_actor(more_text.text_actor, layer=2)

`layer=2` is typically used for text overlay (layer 0 is the background image and layer 1 is used for VTK models).
Finally, we execute the Qt app to show the window:

.. code-block:: python

   overlay_window.show()
   overlay_window.Initialize()
   overlay_window.Start()

   app.exec()
   overlay_window.close()