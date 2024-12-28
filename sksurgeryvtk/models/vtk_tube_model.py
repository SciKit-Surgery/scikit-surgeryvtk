# -*- coding: utf-8 -*-

"""
VTTubeModel creates a VTK pipeline for rendering a list of points as a
set of tubes, based on a vtkPolyLine, and a vtkTubeFilter.
"""

import copy
import numpy as np
import vtk
import sksurgeryvtk.models.vtk_base_model as vbm

# pylint:disable=super-with-arguments


class VTKTubeModel(vbm.VTKBaseModel):
    """
    VTK pipeline to represent a set of points as a vtkPolyLine passed
    through a vtkTubeFilter to produce a tube effect.
    """
    def __init__(self, points, colour, radius=1.0, number_of_sides=50,
                 visibility=True, opacity=1.0,
                 pickable=True, outline=False):
        """
        Creates a new point model.

        :param points: numpy N x 3 array containing x, y, z as float
        :param radius: radius of tube.
        :param number_of_sides: number of sides (rectangles) of each cylinder.
        :param colour: (R,G,B) where each are floats [0-1]
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        :param pickable: boolean, True|False
        :param outline: boolean, do we render a model outline?
        """
        super(VTKTubeModel, self).__init__(colour, visibility, opacity,
                                           pickable, outline)

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
            raise ValueError('radius should be > 0.')
        if number_of_sides <= 0:
            raise ValueError('number_of_sides should be > 0.')

        self.points = copy.deepcopy(points)
        number_of_points = self.points.shape[0]

        self.source = vtk.vtkPolyLineSource()
        self.source.Resize(number_of_points)
        for counter in range(number_of_points):
            self.source.SetPoint(counter,
                                 self.points[counter][0],
                                 self.points[counter][1],
                                 self.points[counter][2])

        self.tube_filter = vtk.vtkTubeFilter()
        self.tube_filter.SetInputConnection(self.source.GetOutputPort())
        self.tube_filter.SetRadius(radius)
        self.tube_filter.SetNumberOfSides(number_of_sides)

        self.triangle_filter = vtk.vtkTriangleFilter()
        self.triangle_filter.SetInputConnection(
            self.tube_filter.GetOutputPort())

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.triangle_filter.GetOutputPort())
        self.mapper.Update()
        self.actor.SetMapper(self.mapper)

    def get_number_of_points(self):
        """
        Returns the number of points described by this tube model.
        :return: number of points
        """
        return self.points.shape[0]

    def set_radius(self, radius):
        """
        Sets the radius of the tubes.
        """
        self.tube_filter.SetRadius(radius)

    def get_radius(self):
        """
        Returns the radius of the tubes.
        :return: radius
        """
        return self.tube_filter.GetRadius()

    def set_number_of_sides(self, number_of_sides):
        """
        Sets the number of sides for each tube.
        """
        self.tube_filter.SetNumberOfSides(number_of_sides)

    def get_number_of_sides(self):
        """
        Returns the number of sides.
        :return: number of sides
        """
        return self.tube_filter.GetNumberOfSides()
