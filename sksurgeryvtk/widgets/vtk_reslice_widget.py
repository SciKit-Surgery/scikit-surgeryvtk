"""
Module to show slice views of volumetric data.
"""
import os
import vtk
import numpy as np
from PySide2 import QtWidgets
from PySide2.QtCore import QTimer

from sksurgeryvtk.widgets.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import cv2
import cv2.aruco as aruco

class VTKResliceWidget(QVTKRenderWindowInteractor):
    
    def __init__(self, reader, axis, parent):

        if axis not in ['x', 'y', 'z']:
            raise TypeError('Argument should be x/y/z')

        super().__init__(parent)
        self.axis = axis

         # Calculate the center of the volume
        self.xMin, self.xMax, self.yMin, self.yMax, self.zMin, self.zMax = \
             reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))
            

        self.xSpacing, self.ySpacing, self.zSpacing = reader.GetOutput().GetSpacing()
        self.x0, self.y0, self.z0 = reader.GetOutput().GetOrigin()

        self.center = [self.x0 + self.xSpacing * 0.5 * (self.xMin + self.xMax),
                self.y0 + self.ySpacing * 0.5 * (self.yMin + self.yMax),
                self.z0 + self.zSpacing * 0.5 * (self.zMin + self.zMax)]

        self.lut = vtk.vtkLookupTable()
        self.lut.SetTableRange(-1000, 1000)
        self.lut.SetHueRange(0, 0)
        self.lut.SetSaturationRange(0, 0)
        self.lut.SetValueRange(0, 1)
        self.lut.Build()

        self.colours = vtk.vtkImageMapToColors()
        self.colours.SetInputConnection(reader.GetOutputPort())
        self.colours.SetLookupTable(self.lut)
        self.colours.Update()

        self.actor = vtk.vtkImageActor()
        self.actor.GetMapper().SetInputConnection(self.colours.GetOutputPort())

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

        self.set_slice_position(0)
        self.renderer.ResetCamera(self.actor.GetBounds())
        self.GetRenderWindow().AddRenderer(self.renderer)

    def set_slice_position(self, position):
        """ Set the slice position in the volume """

        position = int(position)

        if self.axis == 'x':
            position = np.clip(position, self.xMin, self.xMax)
            self.actor.SetDisplayExtent(position, position, self.yMin, self.yMax, self.zMin, self.zMax)

        if self.axis == 'y':
            position = np.clip(position, self.yMin, self.yMax)
            self.actor.SetDisplayExtent(self.xMin, self.xMax, position, position, self.zMin, self.zMax)

        if self.axis == 'z':
            position = np.clip(position, self.zMin, self.zMax)
            self.actor.SetDisplayExtent(self.xMin, self.xMax, self.yMin, self.yMax, position, position)

        # Fill widget with slice by moving camera
        self.renderer.ResetCamera(self.actor.GetBounds())
        self.GetRenderWindow().Render()

class VTKSliceViewer(QtWidgets.QWidget):
    """ Othrogonal slice viewer showing Axial/Sagittal/Coronal views
    :param dicom_dir: path to folder containig dicom data """

    def __init__(self, dicom_dir): 

        super().__init__()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # Start by loading some data.
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(dicom_dir)
        self.reader.Update()

        self.frame = QtWidgets.QFrame()

        self.fourth_panel_renderer = vtk.vtkRenderer()
        self.fourth_panel_renderer.SetBackground(.1, .2, .1)


        self.x = VTKResliceWidget(self.reader, 'x', self.frame)
        self.y = VTKResliceWidget(self.reader, 'y', self.frame)
        self.z = VTKResliceWidget(self.reader, 'z', self.frame)

        self.layout.addWidget(self.x, 0, 0)
        self.layout.addWidget(self.y, 0, 1)
        self.layout.addWidget(self.z, 1, 0)

        self.x.GetRenderWindow().Render()
        self.y.GetRenderWindow().Render()
        self.z.GetRenderWindow().Render()

        self.fourth_panel = QVTKRenderWindowInteractor(self.frame)
        self.fourth_panel.GetRenderWindow().AddRenderer(
            self.fourth_panel_renderer)

        for view in [self.x, self.y, self.z]:
            self.fourth_panel_renderer.AddActor(view.actor)

        self.layout.addWidget(self.fourth_panel, 1, 1)
        self.fourth_panel.GetRenderWindow().Render()

    def update_slice_positions(self, x_pos, y_pos, z_pos):
        """ Set the slice positions for each view.
        :param x: slice 1 position
        :param y: slice 2 position
        :param z: slice 3 position
        """
        self.x.set_slice_position(x_pos)
        self.y.set_slice_position(y_pos)
        self.z.set_slice_position(z_pos)
        self.fourth_panel.GetRenderWindow().Render()


    def reset_slice_positions(self):
        """ Set slcie positions to some default values. """
        self.update_slice_positions(0, 0, 0)



class TrackedSliceViewer(VTKSliceViewer):
    """ Orthogonal slice viewer combined with tracker to
    control slice position.
    :param dicom_dir: Path to folder containing dicom data.
    :param tracker: scikit-surgery tracker object,
                    used to control slice positions """
    def __init__(self, dicom_dir, tracker):

        super().__init__(dicom_dir)
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

            self.update_slice_positions(x, y, z)

    def start(self):
        """Show the overlay widget and
        set a timer running"""

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000.0 / self.update_rate)

        self.show()

        self.reset_slice_positions()
