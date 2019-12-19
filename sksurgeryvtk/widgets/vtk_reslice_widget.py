"""
Module to show slice views of volumetric data.
"""
import vtk
import numpy as np
from PySide2 import QtWidgets

class VTKResliceWidget(QtWidgets.QWidget):

    def __init__(self, volume_data):

        # Start by loading some data.
        self.reader = vtk.vtkImageReader2()
        self.reader.SetFilePrefix( 	"./VTKData/Data/headsq/quarter")
        self.reader.SetDataExtent(0, 63, 0, 63, 1, 93)
        self.reader.SetDataSpacing(3.2, 3.2, 1.5)
        self.reader.SetDataOrigin(0.0, 0.0, 0.0)
        self.reader.SetDataScalarTypeToUnsignedShort()
        self.reader.UpdateWholeExtent()

        # Calculate the center of the volume
        self.reader.Update()
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

        # Create a greyscale lookup table
        self.table = vtk.vtkLookupTable()
        self.table.SetRange(0, 2000) # image intensity range
        self.table.SetValueRange(0.0, 1.0) # from black to white
        self.table.SetSaturationRange(0.0, 0.0) # no color saturation
        self.table.SetRampToLinear()
        self.table.Build()

        actor_axial, renderer_axial, interactor_axial, window_axial = \
            self.create_reslice_view(axial)

        actor_sagittal, renderer_sagittal, interactor_sagittal, window_sagittal = \
            self.create_reslice_view(sagittal)

        actor_coronal, renderer_coronal, interactor_coronal, window_coronal = \
            self.create_reslice_view(coronal)

        window_axial.Render()
        window_sagittal.Render()
        window_coronal.Render()

        interactor_axial.Start()
        interactor_sagittal.Start()
        interactor_coronal.Start()


    def create_reslice_view(self, plane_matrix):
        reslice = vtk.vtkImageReslice()
        reslice.SetInputConnection(self.reader.GetOutputPort())
        reslice.SetOutputDimensionality(2)
        reslice.SetResliceAxes(plane_matrix)
        reslice.SetInterpolationModeToLinear()

        # Map the image through the lookup table
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(self.table)
        color.SetInputConnection(reslice.GetOutputPort())

        # Display the image
        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(color.GetOutputPort())

        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)

        window = vtk.vtkRenderWindow()
        window.AddRenderer(renderer)

        # Set up the interaction
        interactorStyle = vtk.vtkInteractorStyleImage()
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetInteractorStyle(interactorStyle)
        window.SetInteractor(interactor)

        return actor, renderer, interactor, window



VTKResliceWidget(1)