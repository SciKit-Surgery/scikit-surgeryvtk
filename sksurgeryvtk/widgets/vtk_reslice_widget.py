"""
Module to show slice views of volumetric data.
"""
#pylint:disable=too-many-instance-attributes, no-name-in-module
import os
import vtk
import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import QTimer

from vtkmodules.qt.QVTKRenderWindowInteractor \
        import QVTKRenderWindowInteractor


class VTKResliceWidget(QVTKRenderWindowInteractor):
    """ Widget to show a single slice of Volumetric Data.
    :param reader: vtkReader class e.g. DICOM/Niftii/gipl
    :param axis: x/y/z axis selection
    :param parent: parent QWidget.
    """
    def __init__(self, reader, axis, parent):

        if axis not in ['x', 'y', 'z']:
            raise TypeError('Argument should be x/y/z')

        super().__init__(parent)
        self.axis = axis
        self.position = 0
        self.reader = reader

         # Calculate the center of the volume
        self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max \
            = self.reader.GetExecutive().GetWholeExtent(
                self.reader.GetOutputInformation(0))


        self.x_spacing, self.y_spacing, self.z_spacing = \
            self.reader.GetOutput().GetSpacing()
        self.x_0, self.y_0, self.z_0 = self.reader.GetOutput().GetOrigin()

        self.center =\
         [self.x_0 + self.x_spacing * 0.5 * (self.x_min + self.x_max),
          self.y_0 + self.y_spacing * 0.5 * (self.y_min + self.y_max),
          self.z_0 + self.z_spacing * 0.5 * (self.z_min + self.z_max)]

        self.actor = vtk.vtkImageActor()
        self.set_lookup_table_min_max(-1000, 1000)

        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetInput(self.axis)

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.actor)
        self.renderer.AddActor(self.text_actor)

        # Move camera so that the slice is in view
        if axis == "x":
            self.renderer.GetActiveCamera().Azimuth(90)
        if axis == "y":
            self.renderer.GetActiveCamera().Elevation(90)

        self.set_slice_position_mm(0)
        self.renderer.ResetCamera(self.actor.GetBounds())
        self.GetRenderWindow().AddRenderer(self.renderer)

        # Remove unwanted mouse interaction behaviours
        actions = ['MouseWheelForwardEvent', 'MouseWheelBackwardEvent', \
                   'LeftButtonPressEvent', 'RightButtonPressEvent']
        for action in actions:
            self._Iren.RemoveObservers(action)

    def set_lookup_table_min_max(self, min, max):
        #pylint:disable=redefined-builtin
        """ Set the minimum/maximum values for the VTK lookup table i.e.
            change displayed range of intensity values. """

        self.lut = vtk.vtkLookupTable()
        self.lut.SetTableRange(min, max)
        self.lut.SetHueRange(0, 0)
        self.lut.SetSaturationRange(0, 0)
        self.lut.SetValueRange(0, 1)
        self.lut.Build()

        self.colours = vtk.vtkImageMapToColors()
        self.colours.SetInputConnection(self.reader.GetOutputPort())
        self.colours.SetLookupTable(self.lut)
        self.colours.Update()

        self.actor.GetMapper().SetInputConnection(self.colours.GetOutputPort())


    def set_slice_position_pixels(self, pos):
        """ Set the slice position in the volume in pixels """

        pos = int(pos)

        if self.axis == 'x':
            pos = np.clip(pos, self.x_min, self.x_max)
            self.actor.SetDisplayExtent(
                pos, pos, self.y_min, self.y_max, self.z_min, self.z_max)

        if self.axis == 'y':
            pos = np.clip(pos, self.y_min, self.y_max)
            self.actor.SetDisplayExtent(
                self.x_min, self.x_max, pos, pos, self.z_min, self.z_max)

        if self.axis == 'z':
            pos = np.clip(pos, self.z_min, self.z_max)
            self.actor.SetDisplayExtent(
                self.x_min, self.x_max, self.y_min, self.y_max, pos, pos)

        self.position = pos

        # Fill widget with slice by moving camera
        self.renderer.ResetCamera(self.actor.GetBounds())
        self.GetRenderWindow().Render()

    def set_slice_position_mm(self, pos):
        """ Set the slice position in the volume in mm """
        if self.axis == 'x':
            self.set_slice_position_pixels(pos / self.x_spacing)
        if self.axis == 'y':
            self.set_slice_position_pixels(pos / self.y_spacing)
        if self.axis == 'z':
            self.set_slice_position_pixels(pos / self.z_spacing)

    def get_slice_position(self):
        """ Return the current slice position. """
        return self.position

    def reset_position(self):
        """ Set slice position to the middle of the axis. """
        if self.axis == 'x':
            lower, upper = self.x_min, self.x_max
        if self.axis == 'y':
            lower, upper = self.y_min, self.y_max
        if self.axis == 'z':
            lower, upper = self.z_min, self.z_max

        self.set_slice_position_mm(lower + (upper - lower) // 2)


    def on_mouse_wheel_forward(self, obj, event):
        #pylint:disable=unused-argument
        """ Callback to change slice position using mouse wheel. """
        current_position = self.get_slice_position()
        self.set_slice_position_pixels(current_position + 1)

    def on_mouse_wheel_backward(self, obj, event):
        #pylint:disable=unused-argument
        """ Callback to change slice position using mouse wheel. """
        current_position = self.get_slice_position()
        self.set_slice_position_pixels(current_position - 1)

    def set_mouse_wheel_callbacks(self):
        """ Add callbacks for scroll events. """
        self._Iren.AddObserver('MouseWheelForwardEvent',
                               self.on_mouse_wheel_forward)

        self._Iren.AddObserver('MouseWheelBackwardEvent',
                               self.on_mouse_wheel_backward)


class VTKSliceViewer(QtWidgets.QWidget):
    """ Othrogonal slice viewer showing Axial/Sagittal/Coronal views
    :param input_data: path to volume data """

    def __init__(self, input_data):

        super().__init__()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # Start by loading some data.
        if os.path.isdir(input_data):
            self.reader = vtk.vtkDICOMImageReader()
            self.reader.SetDirectoryName(input_data)

        elif input_data.endswith(('.nii', '.nii.gz')):
            self.reader = vtk.vtkNIFTIImageReader()
            self.reader.SetFileName(input_data)

        self.reader.Update()

        self.frame = QtWidgets.QFrame()

        self.fourth_panel_renderer = vtk.vtkRenderer()
        self.fourth_panel_renderer.SetBackground(.1, .2, .1)


        self.x_view = VTKResliceWidget(self.reader, 'x', self.frame)
        self.y_view = VTKResliceWidget(self.reader, 'y', self.frame)
        self.z_view = VTKResliceWidget(self.reader, 'z', self.frame)

        self.layout.addWidget(self.x_view, 0, 0)
        self.layout.addWidget(self.y_view, 0, 1)
        self.layout.addWidget(self.z_view, 1, 0)

        self.x_view.GetRenderWindow().Render()
        self.y_view.GetRenderWindow().Render()
        self.z_view.GetRenderWindow().Render()

        self.fourth_panel = QVTKRenderWindowInteractor(self.frame)
        self.fourth_panel.GetRenderWindow().AddRenderer(
            self.fourth_panel_renderer)

        for view in [self.x_view, self.y_view, self.z_view]:
            self.fourth_panel_renderer.AddActor(view.actor)

        self.layout.addWidget(self.fourth_panel, 1, 1)
        self.fourth_panel.GetRenderWindow().Render()

    def set_lookup_table_min_max(self, min, max):
        #pylint:disable=redefined-builtin
        """ Set lookup table min/max for all slice views """
        self.x_view.set_lookup_table_min_max(min, max)
        self.y_view.set_lookup_table_min_max(min, max)
        self.z_view.set_lookup_table_min_max(min, max)

    def update_slice_positions_mm(self, x_pos, y_pos, z_pos):
        """ Set the slice positions for each view.
        :param x: slice 1 position
        :param y: slice 2 position
        :param z: slice 3 position
        """
        self.x_view.set_slice_position_mm(x_pos)
        self.y_view.set_slice_position_mm(y_pos)
        self.z_view.set_slice_position_mm(z_pos)
        self.fourth_panel.GetRenderWindow().Render()

    def update_slice_positions_pixels(self, x_pos, y_pos, z_pos):
        """ Set the slice positions for each view.
        :param x: slice 1 position
        :param y: slice 2 position
        :param z: slice 3 position
        """
        self.x_view.set_slice_position_pixels(x_pos)
        self.y_view.set_slice_position_pixels(y_pos)
        self.z_view.set_slice_position_pixels(z_pos)
        self.fourth_panel.GetRenderWindow().Render()

    def reset_slice_positions(self):
        """ Set slcie positions to some default values. """
        self.x_view.reset_position()
        self.y_view.reset_position()
        self.z_view.reset_position()
        self.fourth_panel.GetRenderWindow().Render()



class MouseWheelSliceViewer(VTKSliceViewer):
    """ Orthogonal slice viewer using mouse wheel to
    control slice position.

    Example usage:

    qApp = QtWidgets.QApplication([])
    input_data = 'tests/data/dicom/LegoPhantom_10slices'

    slice_viewer = MouseWheelSliceViewer(input_data)
    slice_viewer.start()
    qApp.exec_()

    """

    def __init__(self, input_data):

        super().__init__(input_data)

        self.x_view.set_mouse_wheel_callbacks()
        self.y_view.set_mouse_wheel_callbacks()
        self.z_view.set_mouse_wheel_callbacks()

        self.update_rate = 20

    def update_fourth_panel(self):
        """ Update 3D view. """
        self.fourth_panel.GetRenderWindow().Render()

    def start(self):
        #pylint:disable=attribute-defined-outside-init, no-member
        """ Start a timer which will update the 3D view. """

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fourth_panel)
        self.timer.start(1000.0 / self.update_rate)

        self.show()
        self.reset_slice_positions()


class TrackedSliceViewer(VTKSliceViewer):
    #pylint:disable=invalid-name
    """ Orthogonal slice viewer combined with tracker to
    control slice position.
    :param input_data: Path to file/folder containing volume data
    :param tracker: scikit-surgery tracker object,
                    used to control slice positions.

    Example usage:

    qApp = QtWidgets.QApplication([])
    input_data = 'tests/data/dicom/LegoPhantom_10slices'
    tracker = ArUcoTracker()

    slice_viewer = MouseWheelSliceViewer(input_data, tracker)
    slice_viewer.start()
    qApp.exec_()

    """
    def __init__(self, input_data, tracker):

        super().__init__(input_data)
        self.tracker = tracker
        self.update_rate = 20

    def update_position(self):
        """ Get position from tracker and use this
        to set slice positions. """
        _, _, _, tracking_data, _ = self.tracker.get_frame()

        if tracking_data is not None:
            x, y, z = tracking_data[0][0][3], \
                      tracking_data[0][1][3], \
                      tracking_data[0][2][3]

            self.update_slice_positions_mm(x, y, z)

    def start(self):
        #pylint:disable=attribute-defined-outside-init, no-member
        """Show the overlay widget and
        set a timer running"""

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000.0 / self.update_rate)

        self.show()

        self.reset_slice_positions()
