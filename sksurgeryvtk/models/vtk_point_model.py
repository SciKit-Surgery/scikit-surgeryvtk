# -*- coding: utf-8 -*-

"""
VTK pipeline to represent a point model via a vtkPolyData with a separate
(RGB) component for each point, such that each point is rendered with the
correct colour. Note that this model is designed to have a fixed number
of points. If you want varying number of points for each render pass,
you should consider another way of doing this.
"""

import numpy as np
import vtk
from vtk.util import numpy_support
import sksurgeryvtk.models.vtk_base_model as vbm

#pylint:disable=super-with-arguments

class VTKPointModel(vbm.VTKBaseModel):
    """
    Class to represent a VTK point model. Note, that if
    """
    def __init__(self, points, colours,
                 visibility=True, opacity=1.0):
        """
        Creates a new point model.

        :param points: numpy N x 3 array containing x, y, z as float
        :param colours: numpy N x 3 array containing RGB as [0-255] uchar
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        """
        super(VTKPointModel, self).__init__((1.0, 1.0, 1.0),
                                            visibility,
                                            opacity)

        # Validate as much as possible, up front.
        if points is None:
            raise ValueError('points is None.')
        if colours is None:
            raise ValueError('colours is None.')
        if not isinstance(points, np.ndarray):
            raise TypeError('points is not a numpy array.')
        if not isinstance(colours, np.ndarray):
            raise TypeError('colours is not a numpy array.')
        if points.shape[1] != 3:
            raise ValueError('points should have 3 columns.')
        if colours.shape[1] != 3:
            raise ValueError('colours should have 3 columns.')
        if points.shape[0] == 0:
            raise ValueError('points should have > 0 rows.')
        if colours.shape[0] == 0:
            raise ValueError('colours should have > 0 rows.')
        if colours.shape != points.shape:
            raise ValueError('points and colours should have the same shape.')
        if points.dtype != np.float:
            raise TypeError('points should be float type.')
        if colours.dtype != np.byte:
            raise TypeError('colours should be byte (unsigned char) type.')

        self.points = points
        self.colours = colours

        self.vtk_point_array = numpy_support.numpy_to_vtk(
            num_array=self.points, deep=True, array_type=vtk.VTK_FLOAT)

        self.vtk_colours_array = numpy_support.numpy_to_vtk(
            num_array=self.colours, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        self.vtk_colours_array.SetName('Colours')

        self.vtk_points = vtk.vtkPoints()
        self.vtk_points.SetData(self.vtk_point_array)

        number_of_points = points.shape[0]
        cells = np.hstack((np.ones((number_of_points, 1), dtype=np.int64),
                           np.arange(number_of_points).reshape(-1, 1)))
        cells = np.ascontiguousarray(cells, dtype=np.int64)
        cell_array = numpy_support.numpy_to_vtk(
            num_array=cells, deep=True, array_type=vtk.VTK_ID_TYPE)

        self.vtk_cells = vtk.vtkCellArray()
        self.vtk_cells.SetCells(number_of_points, cell_array)

        self.vtk_poly = vtk.vtkPolyData()
        self.vtk_poly.SetPoints(self.vtk_points)
        self.vtk_poly.SetVerts(self.vtk_cells)
        self.vtk_poly.GetPointData().SetScalars(self.vtk_colours_array)

        self.vtk_mapper = vtk.vtkPolyDataMapper()
        self.vtk_mapper.SetInputData(self.vtk_poly)
        self.actor.SetMapper(self.vtk_mapper)
        self.actor.GetProperty().SetPointSize(5)

    def get_number_of_points(self):
        """
        Returns the number of points (hence vertices) in the model.
        :return: number of points
        """
        return self.vtk_points.GetNumberOfPoints()

    def set_point_size(self, size):
        """
        Sets the size of each point in pixels.
        """
        self.actor.GetProperty().SetPointSize(size)

    def get_point_size(self):
        """
        Returns the current point size in pixels.
        :return: size
        """
        return self.actor.GetProperty().GetPointSize()
