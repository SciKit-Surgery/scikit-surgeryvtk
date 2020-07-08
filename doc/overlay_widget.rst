.. _OverlayWidget:

How to Use VTKOverlayWindow
===========================

This library provides a simple PySide2/VTK widget called VTKOverlayWindow for doing simple
augmented reality (AR) overlays, using calibrated parameters, like those obtained
from OpenCV. The video image is rendered as a background layer,
with VTK models as a foreground layer. This is not very photo-realistic,
but most researchers are focussing on registration/alignment rather than true 3D perception.

In this page, we show how to use VTKOverlayWindow.


Simple Usage
------------

This explanation is based on the unit test ```tests/camera/test_vtk_camera_model.py::test_camera_projection``` which
has a picture of a chessboard, a model of the 4 corners in chessboard coordinates,
a set of intrinsic and extrinsic camera parameters derived from OpenCV, and
can overlay the 3D model (chessboard corners) on-top of the video, in the correct
position.

Background Image
^^^^^^^^^^^^^^^^

The VTKOverlayWidget can be used to display a video image, centred in the
screen. Assuming some code has created a QApplication context, then you:

::

  widget = VTKOverlayWindow()
  widget.set_video_image(undistorted_rgb_image)
  widget.show()

and then, you can repeatedly set the video image in a render loop.

::

  while(True):
    rgb_image = # grab image somehow.
    undistorted_rgb_image = cv2.undistort(...)
    widget.set_video_image(undistorted_rgb_image)

The window can be resized, and the video image stays centred. It is rendered
in its own layer, as a background layer.

Note that VTK requires RGB, whereas OpenCV defaults to BGR. So, as this
library is primarily based on VTK, the input is assumed to be RGB.

Set Camera Parameters
^^^^^^^^^^^^^^^^^^^^^

If you want to use a calibrated camera, it is assumed that the rendering
is to be done in undistorted space. So, the above example suggested
that you provide an undistorted RGB image to the widget.
This means that to get a correct AR overlay, you simply need to set the
camera intrinsic parameters, and the camera extrinsics (pose, position and orientation).

The extrinsics are defined as being the camera_to_world matrix, i.e. to place the camera
at the correct position in the world. If you are trying to set the pose
to verify an OpenCV camera calibration, and are using the OpenCV extrinsic matrix
from the calibration process, then this is in effect a transformation from model (chessboard)
to camera, so you'd need to invert it the OpenCV extrinsic matrix.

So, a more complete example is:

::

  widget = VTKOverlayWindow()
  widget.set_camera_matrix(intrinsics) # where 'intrinsics' is 3x3 ndarray of camera intrinsic parameters
  widget.show()

  while(True):

    undistorted_rgb_image = # get undistorted RGB image somehow.
    widget.set_video_image(undistorted_rgb_image)

    camera_to_world = # compute camera to world transform
    widget.set_camera_pose(camera_to_world)

The intrinsics will likely only need setting once, when the calibration
is loaded. The camera-to-world will need setting at each rendering update.

The end result of the unit test is shown below.

.. image:: overlay_window.png
  :width: 50%

3D model coordinates of the 4 corners are constructed into a plane, and projected back on the original video image using OpenCV calibration parameters.


How It Works
------------

  - Putting the background image in the correct place: `VTKOverlayWindow::__update_video_image <https://github.com/UCL/scikit-surgeryvtk/blob/master/sksurgeryvtk/widgets/vtk_overlay_window.py#L200>`_.
  - Setting the camera pose `vtk_camera_model::set_camera_pose <https://github.com/UCL/scikit-surgeryvtk/blob/master/sksurgeryvtk/camera/vtk_camera_model.py#L143>`_.
  - Setting the intrinsics `VTKOverlayWindow::__update_projection_matrix <https://github.com/UCL/scikit-surgeryvtk/blob/master/sksurgeryvtk/widgets/vtk_overlay_window.py#L238>`_.





