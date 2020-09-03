# -*- coding: utf-8 -*-

"""
VTK pipeline to represent a surface model via a vtkPolyData.
"""
import vtk
import sksurgeryvtk.models.vtk_surface_model as vbs

#pylint:disable=super-with-arguments

class VTKCylinderModel(vbs.VTKSurfaceModel):
    """
    Class to create a VTK surface model of a cylinder.
    """
    def __init__(self, height=10.0, radius=3.0,
                 colour=(1., 0., 0.), name="cylinder",
                 angle=90.0, orientation=(1., 0., 0.),
                 resolution=88,
                 visibility=True, opacity=1.0):
        """
        Creates a new cylinder model.

        :param height: the height of the cylinder
        :param radius: the radius of the cylinder
        :param colour: (R,G,B) where each are floats [0-1]
        :param name: a name for the model
        :param angle: Angle in degrees rotate cylinder
        :param orientation: Orientation vector for angle
        :param resolution
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        """

        super(VTKCylinderModel, self).__init__(None, colour, visibility,
                                               opacity)
        self.name = name

        cyl = vtk.vtkCylinderSource()
        cyl.SetResolution(resolution)
        cyl.SetRadius(radius)
        cyl.SetHeight(height)
        cyl.Update()
        self.source = cyl.GetOutput()

        rotation = vtk.vtkTransform()
        rotation.RotateWXYZ(angle, orientation)
        self.transform_filter = vtk.vtkTransformPolyDataFilter()
        self.transform_filter.SetInputData(self.source)
        self.transform_filter.SetTransform(rotation)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.transform_filter.GetOutputPort())
        self.mapper.Update()
        self.actor.SetMapper(self.mapper)
