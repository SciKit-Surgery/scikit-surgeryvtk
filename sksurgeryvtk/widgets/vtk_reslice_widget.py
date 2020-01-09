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

class ArucoTracker:

    def __init__(self, image_source):
        #the aruco tag dictionary to use. DICT_4X4_50 will work with the tag in
        #../tags/aruco_4by4_0.pdf
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        # The size of the aruco tag in mm
        self.marker_size = 50

        #we'll use opencv to estimate the pose of the visible aruco tags.
        #for that we need a calibrated camera. For now let's just use a
        #a hard coded estimate. Maybe you could improve on this.
        self.camera_projection_mat = np.array([[560.0, 0.0, 320.0],
                                                  [0.0, 560.0, 240.0],
                                                  [0.0, 0.0, 1.0]])
        self.camera_distortion = np.zeros((1, 4), np.float32)

        self.cap = cv2.VideoCapture(image_source)

        self.tvecs = None

    def update(self):
        ret, img = self.cap.read()
        self._aruco_detect_and_follow(img)
        cv2.waitKey(1)

        if self.tvecs is not None:
            return self.tvecs[0][0]

        return None

    def _aruco_detect_and_follow(self, image):
        """Detect any aruco tags present. Based on;
        https://docs.opencv.org/3.4/d5/dae/tutorial_aruco_detection.html
        """
        #detect any markers
        marker_corners, _, _ = aruco.detectMarkers(image, self.dictionary)

        if marker_corners:
            #if any markers found, try and determine their pose
            self.rvecs, self.tvecs, _ = \
                    aruco.estimatePoseSingleMarkers(marker_corners,
                                                    self.marker_size,
                                                    self.camera_projection_mat,
                                                    self.camera_distortion)


class VTKSliceViewer(QtWidgets.QWidget):
    """ Othrogonal slice viewer showing Axial/Sagittal/Coronal views
    :param dicom_dir: path to folder containig dicom data """

    def __init__(self, dicom_dir): 

        super().__init__()

        self.layout = QtWidgets.QGridLayout()
        # Start by loading some data.
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(dicom_dir)
        self.reader.Update()

        self.frame = QtWidgets.QFrame()
        self.x = SimpleVTKResliceWidget(self.reader, 'x', self.frame)
        self.y = SimpleVTKResliceWidget(self.reader, 'y', self.frame)
        self.z = SimpleVTKResliceWidget(self.reader, 'z', self.frame)

        self.layout.addWidget(self.x, 0, 0)
        self.layout.addWidget(self.y, 0, 1)
        self.layout.addWidget(self.z, 1, 0)

        self.setLayout(self.layout)
        self.x.GetRenderWindow().Render()
        self.y.GetRenderWindow().Render()
        self.z.GetRenderWindow().Render()

        self.fourth_panel = QVTKRenderWindowInteractor(self.frame)
       
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(.1, .2, .1)
        self.fourth_panel.GetRenderWindow().AddRenderer(self.renderer)

        for v in [self.x, self.y, self.z]:
            self.renderer.AddActor(v.actor)

        self.layout.addWidget(self.fourth_panel, 1, 1)
        self.fourth_panel.GetRenderWindow().Render()

    def update_slice_positions(self, x_pos, y_pos, z_pos):
        """ Set the slice positions for each view.
        :param x: slice 1 position
        :param y: slice 2 position
        :param z: slice 3 position
        """
        self.z.set_slice_position(z_pos)
        self.x.set_slice_position(x_pos)
        self.y.set_slice_position(y_pos)


        self.fourth_panel.GetRenderWindow().Render()


    def reset_slice_positions(self):
        """ Set slcie positions to some default values. """
        self.update_slice_positions(0, 0, 0)

class SimpleVTKResliceWidget(QVTKRenderWindowInteractor):
    
    def __init__(self, reader, axis, parent):

        if axis not in ['x', 'y', 'z']:
            raise TypeError('Argument should be axial/sagittal/coronal')

        super().__init__(parent)
        self.axis = axis

         # Calculate the center of the volume
        (self.xMin, self.xMax, self.yMin, self.yMax, self.zMin, self.zMax) = \
             reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))

        (self.xSpacing, self.ySpacing, self.zSpacing) = reader.GetOutput().GetSpacing()
        # (self.x0, self.y0, self.z0) = reader.GetOutput().GetOrigin()

        # self.center = [self.x0 + self.xSpacing * 0.5 * (self.xMin + self.xMax),
        #         self.y0 + self.ySpacing * 0.5 * (self.yMin + self.yMax),
        #         self.z0 + self.zSpacing * 0.5 * (self.zMin + self.zMax)]
        print(f'x: {self.xMin} {self.xMax} {self.zSpacing}\n \
         y:{self.yMin} {self.yMax} {self.ySpacing}\n \
         z: {self.zMin} {self.zMax} {self.zSpacing}')
        self.lut = vtk.vtkLookupTable()
        self.lut.SetTableRange(-1000,1000)
        self.lut.SetHueRange(0,0)
        self.lut.SetSaturationRange(0,0)
        self.lut.SetValueRange(0,1)
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

        self.set_slice_position(0)
        self.renderer.ResetCamera(self.actor.GetBounds())
        if axis == 'y':
            self.renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
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
            position = position // 10
            position = np.clip(position, self.zMin, self.zMax)
            self.actor.SetDisplayExtent(self.xMin, self.xMax, self.yMin, self.yMax, position, position)
       
        # print(self.axis)
        # print(cam.GetViewUp())
        # print(cam.GetFocalPoint())
        # print(cam.GetPosition())

        #self.renderer.ResetCamera(self.actor.GetBounds())
        cam = self.renderer.GetActiveCamera()


        self.GetRenderWindow().Render()


class VTKResliceWidget(QVTKRenderWindowInteractor):
    """" Single slice view
    :param reader: vtk reader object containing data to be displayed
    :param plane_matrix: matrix which sets the slice orientation
    :param parent: parent widget used in init method of QVTKRenderWindowInteractor
    """

    def __init__(self, reader, axis, parent):
        super().__init__(parent)

        self.axis = axis
        # Calculate the center of the volume
        (self.xMin, self.xMax, self.yMin, self.yMax, self.zMin, self.zMax) = \
             reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))

        (xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
        (self.x0, self.y0, self.z0) = reader.GetOutput().GetOrigin()

        center = [self.x0 + xSpacing * 0.5 * (self.xMin + self.xMax),
                self.y0 + ySpacing * 0.5 * (self.yMin + self.yMax),
                self.z0 + zSpacing * 0.5 * (self.zMin + self.zMax)]

        # Matrices for x, y and z view orientations
        y = vtk.vtkMatrix4x4()
        y.DeepCopy((1, 0, 0, center[0],
                        0, 1, 0, center[1],
                        0, 0, 1, center[2],
                        0, 0, 0, 1))

        x = vtk.vtkMatrix4x4()
        x.DeepCopy((1, 0, 0, center[0],
                        0, 0, 1, center[1],
                        0,-1, 0, center[2],
                        0, 0, 0, 1))

        z = vtk.vtkMatrix4x4()
        z.DeepCopy((0, 0,-1, center[0],
                        1, 0, 0, center[1],
                        0,-1, 0, center[2],
                        0, 0, 0, 1))

        if plane == 'y':
            plane_matrix = y
            self.lower, self.upper = self.yMin, self.yMax
            self.spacing = ySpacing
            self.origin = self.y0
        
        elif plane == 'z':
            plane_matrix = z
            self.lower, self.upper = self.zMin, self.zMax
            self.spacing = zSpacing
            self.origin = self.z0

        elif plane == 'x':
            plane_matrix = x
            self.lower, self.upper = self.xMin, self.xMax
            self.spacing = xSpacing
            self.origin = self.x0

        else:
            raise TypeError('Argument should be axial/sagittal/coronal')

        self.intensity_min  = -1000
        self.intensity_max = 1000 #TODO
        # Create a greyscale lookup table
        self.table = vtk.vtkLookupTable()
        self.table.SetRange(self.intensity_min, self.intensity_max) # image intensity range
        self.table.SetValueRange(0.0, 1.0) # from black to white
        self.table.SetSaturationRange(0.0, 0.0) # no color saturation
        self.table.SetRampToLinear()
        self.table.Build()

        self.reslice = vtk.vtkImageReslice()
        self.reslice.SetInputConnection(reader.GetOutputPort())
        self.reslice.SetOutputDimensionality(2)
        self.reslice.SetResliceAxes(plane_matrix)
        self.reslice.SetInterpolationModeToLinear()

        # Map the image through the lookup table
        self.color = vtk.vtkImageMapToColors()
        self.color.SetLookupTable(self.table)
        self.color.SetInputConnection(self.reslice.GetOutputPort())

        # Display the image
        self.actor = vtk.vtkImageActor()
        self.actor.GetMapper().SetInputConnection(self.color.GetOutputPort())

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.actor)

        self.GetRenderWindow().AddRenderer(self.renderer)

        # Set up the interaction
        self.interactorStyle = vtk.vtkInteractorStyleImage()
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(self.interactorStyle)
        self.GetRenderWindow().SetInteractor(self.interactor)

    def set_slice_position(self, position):
        """ Set the slice position in the volume """

        np.clip(position, self.lower, self.upper)
        self.reslice.Update()
        matrix = self.reslice.GetResliceAxes()

        if self.axis == 'z':
            matrix.SetElement(0, 3, position)
        if self.axis == 'x':
            matrix.SetElement(1, 3, position)
        if self.axis == 'y':
            matrix.SetElement(2, 3, position)
        self.GetRenderWindow().Render()


class TrackedSliceViewer(VTKSliceViewer):
    """ Orthogonal slice viewer combined with tracker to
    control slice position.
    :param dicom_dir: Path to folder containing dicom data.
    :param tracker: Tracker object used to control slice positions """
    def __init__(self, dicom_dir, tracker):

        super().__init__(dicom_dir)
        self.tracker = tracker
        self.update_rate = 20

    def update_position(self):
        """ Get position from tracker and use this
        to set slice positions. """
        ret = self.tracker.update()

        if ret is not None:
            x,y,z = ret
            self.update_slice_positions(x,y,z)

    def start(self):
        """Show the overlay widget and
        set a timer running"""

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000.0 / self.update_rate)

        self.show()

        self.reset_slice_positions()


qApp = QtWidgets.QApplication([])

tracker = ArucoTracker(0)
dicom_path = 'tests/data/dicom/LegoPhantom'
slice_viewer = TrackedSliceViewer(dicom_path, tracker)
slice_viewer.start()

qApp.exec_()


# def MouseMoveCallback(self, obj, event):
#     mouseX, mouseY = self.interactor.GetEventPosition()
#     screenX, screenY = self.window.GetSize()
#     percentX = 100.0 * mouseX/screenX
#     percentY = 100.0 * mouseY/screenY

# position = self.lower + self.spacing * (self.upper - self.lower) * percent / 100
# print(f'{self.axis} {self.upper} Position: {position}')