# -*- coding: utf-8 -*-

"""
VTK pipeline to represent a surface model via a vtkPolyData.
"""

import os
import vtk
from vtk.util import numpy_support
import sksurgerycore.utilities.validate_file as vf
import sksurgeryvtk.models.vtk_base_model as vbm
import sksurgeryvtk.utils.matrix_utils as mu

# pylint: disable=no-member


class VTKSurfaceModel(vbm.VTKBaseModel):
    """
    Class to represent a VTK surface model. Normally
    read from a file, but could be created on the fly.
    """
    def __init__(self, filename, colour, visibility=True, opacity=1.0):
        """
        Creates a new surface model.

        :param filename: if None a default, empty, vtkPolyData is created.
        :param colour: (R,G,B) where each are floats [0-1]
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        """
        super(VTKSurfaceModel, self).__init__(colour, visibility, opacity)

        self.source_file = None
        self.reader = None
        self.source = None

        # Works like FactoryMethod. Could be refactored elsewhere.
        if filename is not None:

            vf.validate_is_file(filename)

            if filename.endswith('.vtk'):
                self.reader = vtk.vtkPolyDataReader()

            elif filename.endswith('.stl'):
                self.reader = vtk.vtkSTLReader()

            elif filename.endswith('.ply'):
                self.reader = vtk.vtkPLYReader()

            elif filename.endswith('.vtp'):
                self.reader = vtk.vtkXMLPolyDataReader()
            else:
                raise ValueError(
                    'File type not supported for model loading: {}'.format(
                        filename))

            self.reader.SetFileName(filename)
            self.reader.Update()
            self.source = self.reader.GetOutput()

            self.source_file = filename
            self.name = os.path.basename(self.source_file)
        else:
            # Creates a new empty vtkPolyData, that the client
            # can dynamically fill with new data.
            self.source = vtk.vtkPolyData()
            self.name = ""

        # Only create normals if there are none on input
        self.normals = None
        if self.source.GetPointData().GetNormals() is None:
            self.normals = vtk.vtkPolyDataNormals()
            self.normals.SetInputData(self.source)
            self.normals.SetAutoOrientNormals(True)
            self.normals.SetFlipNormals(False)
        self.transform = vtk.vtkTransform()
        self.transform.Identity()
        self.transform_filter = vtk.vtkTransformPolyDataFilter()
        if self.normals is None:
            self.transform_filter.SetInputData(self.source)
        else:
            self.transform_filter.SetInputConnection(
                self.normals.GetOutputPort())
        self.transform_filter.SetTransform(self.transform)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.transform_filter.GetOutputPort())
        self.mapper.Update()
        self.actor.SetMapper(self.mapper)

    def set_model_transform(self, matrix):
        """
        Sets the model to world transform onto a vtkPolyDataFilter.
        This enables all the points and point data to be transformed
        according to a vtkMatrix4x4 similarity transform.
        :param matrix: vtkMatrix4x4
        """
        mu.validate_vtk_matrix_4x4(matrix)
        self.transform.SetMatrix(matrix)
        self.transform_filter.SetTransform(self.transform)

    def get_model_transform(self):
        """
        Gets the model to world transform.
        :return: vtkMatrix4x4
        """
        return self.transform.GetMatrix()

    def get_number_of_points(self):
        """
        Returns the number of points in the vtkPoylData.
        :return: unsigned int
        """
        self.transform_filter.Update()
        number_of_points = self.transform_filter.GetOutput().GetNumberOfPoints()
        return number_of_points

    def get_points_as_numpy(self):
        """
        Returns the vtkPolyData points as a numpy array.
        :return: nx3 numpy ndarray
        """
        self.transform_filter.Update()
        vtk_points = self.transform_filter.GetOutput().GetPoints()
        as_numpy = numpy_support.vtk_to_numpy(vtk_points.GetData())
        return as_numpy

    def get_normals_as_numpy(self):
        """
         Returns the vtkPolyData point normals as a numpy array.
        :return: nx3 numpy ndarray
        """
        self.transform_filter.Update()
        vtk_normals = self.transform_filter \
            .GetOutput().GetPointData().GetNormals()
        as_numpy = numpy_support.vtk_to_numpy(vtk_normals)
        return as_numpy
