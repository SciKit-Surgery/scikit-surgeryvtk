# -*- coding: utf-8 -*-

"""
VTKSphereModel creates a VTK pipeline to represent a set of points,
as sphere glyphs.
"""

import numpy as np
import vtk
from vtk.util import numpy_support

import sksurgeryvtk.models.vtk_base_model as vbm

# pylint:disable=super-with-arguments


class VTKSphereModel(vbm.VTKBaseModel):
    """
    Class to represent a set of points as sphere glyphs (one sphere per point).
    """
    def __init__(self, points, radius, colour=(1.0, 1.0, 1.0),
                 visibility=True, opacity=1.0,
                 pickable=True, resolution = 12):
        """
        Creates a new sphere model.

        :param points: numpy N x 3 array containing x, y, z as float
        :param colour: (R,G,B) where each are floats [0-1]
        :param radius: sphere radius in millimetres
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        :param pickable: boolean, True|False
        :param resolution: the resolution (theta and phy)
        """
        super(VTKSphereModel, self).__init__(colour, visibility, opacity,
                                             pickable)

        # Validate as much as possible, up front.
        if points is None:
            raise ValueError('points is None.')
        if not isinstance(points, np.ndarray):
            raise TypeError('points is not a numpy array.')
        if points.shape[1] != 3:
            raise ValueError('points should have 3 columns.')
        if points.shape[0] == 0:
            raise ValueError('points should have > 0 rows.')
        if points.dtype != float:
            raise TypeError('points should be float type.')
        if radius <= 0:
            raise ValueError('sphere radius should >= 0.')

        self.points = points
        self.vtk_point_array = numpy_support.numpy_to_vtk(
            num_array=self.points, deep=True, array_type=vtk.VTK_FLOAT)
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

        self.vtk_sphere = vtk.vtkSphereSource()
        self.vtk_sphere.SetRadius(radius)
        self.vtk_sphere.SetPhiResolution(resolution)
        self.vtk_sphere.SetThetaResolution(resolution)

        self.vtk_glyph = vtk.vtkGlyph3D()
        self.vtk_glyph.SetSourceConnection(self.vtk_sphere.GetOutputPort())
        self.vtk_glyph.SetInputData(self.vtk_poly)
        self.vtk_glyph.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.vtk_glyph.GetOutputPort())
        self.mapper.Update()
        self.actor.SetMapper(self.mapper)
