"""
Module to show slice views of volumetric data.
"""
import os
import vtk
import numpy as np
from PySide2 import QtWidgets

class VTKSliceViewer(QtWidgets.QWidget):
    """ Othrogonal slice viewer showing Axial/Sagittal/Coronal views """

    def __init__(self, dicom_dir):

        # Start by loading some data.
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(dicom_dir)
        self.reader.Update()

        # Calculate the center of the volume
        (xMin, xMax, yMin, yMax, zMin, zMax) = self.reader.GetExecutive().GetWholeExtent(self.reader.GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = self.reader.GetOutput().GetSpacing()
        (x0, y0, z0) = self.reader.GetOutput().GetOrigin()

        center = [x0 + xSpacing * 0.5 * (xMin + xMax),
                y0 + ySpacing * 0.5 * (yMin + yMax),
                z0 + zSpacing * 0.5 * (zMin + zMax)]

        # Matrices for axial, coronal, sagittal view orientations
        axial = vtk.vtkMatrix4x4()
        axial.DeepCopy((1, 0, 0, center[0],
                        0, 1, 0, center[1],
                        0, 0, 1, center[2],
                        0, 0, 0, 1))

        coronal = vtk.vtkMatrix4x4()
        coronal.DeepCopy((1, 0, 0, center[0],
                        0, 0, 1, center[1],
                        0,-1, 0, center[2],
                        0, 0, 0, 1))

        sagittal = vtk.vtkMatrix4x4()
        sagittal.DeepCopy((0, 0,-1, center[0],
                        1, 0, 0, center[1],
                        0,-1, 0, center[2],
                        0, 0, 0, 1))

        axial = VTKResliceWidget(self.reader, axial)
        sagittal = VTKResliceWidget(self.reader, sagittal)
        coronal = VTKResliceWidget(self.reader, coronal)

        axial.window.Render()
        sagittal.window.Render()
        coronal.window.Render()

        axial.interactor.Start()
        sagittal.interactor.Start()
        coronal.interactor.Start()


class VTKResliceWidget(QtWidgets.QWidget):
    """" Single slice view
    :param reader: vtk reader object containing data to be displayed
    :param plane_matrix: matrix which sets the slice orientation
    """

    def __init__(self, reader, plane_matrix):
        
        self.intensity_max = 1000
        # Create a greyscale lookup table
        self.table = vtk.vtkLookupTable()
        self.table.SetRange(0, self.intensity_max) # image intensity range
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

        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)

        # Set up the interaction
        self.interactorStyle = vtk.vtkInteractorStyleImage()
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(self.interactorStyle)
        self.window.SetInteractor(self.interactor)

        # Create callbacks for slicing the image
        self.actions = {}
        self.actions["Slicing"] = 0

        self.interactorStyle.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        self.interactorStyle.AddObserver("LeftButtonPressEvent", self.ButtonCallback)
        self.interactorStyle.AddObserver("LeftButtonReleaseEvent", self.ButtonCallback)

    def ButtonCallback(self, obj, event):
        if event == "LeftButtonPressEvent":
            self.actions["Slicing"] = 1
        else:
            self.actions["Slicing"] = 0

    def MouseMoveCallback(self, obj, event):
        (lastX, lastY) = self.interactor.GetLastEventPosition()
        (mouseX, mouseY) = self.interactor.GetEventPosition()
        if self.actions["Slicing"] == 1:
            deltaY = mouseY - lastY
            self.reslice.Update()
            sliceSpacing = self.reslice.GetOutput().GetSpacing()[2]
            matrix = self.reslice.GetResliceAxes()
            # move the center point that we are slicing through
            center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
            matrix.SetElement(0, 3, center[0])
            matrix.SetElement(1, 3, center[1])
            matrix.SetElement(2, 3, center[2])
            self.window.Render()
        else:
            self.interactorStyle.OnMouseMove()



VTKSliceViewer('tests/data/dicom/LegoPhantom')