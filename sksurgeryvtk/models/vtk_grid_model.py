# -*- coding: utf-8 -*-

"""
VTK pipeline to represent a vtkUnstructredGrid.
"""

import os
from typing import Tuple

import numpy as np
import vtk
from vtk.util import numpy_support
import sksurgerycore.utilities.validate_file as vf
import sksurgeryvtk.models.vtk_base_model as vbm

# pylint: disable=too-many-instance-attributes
# pylint: disable=super-with-arguments, dangerous-default-value

class VTKUnstructuredGridModel(vbm.VTKBaseModel):
    """
    Class to represent a VTK grid model read from a file.
    """
    def __init__(self, filename, colour=[1.0, 0.0, 0.0],
                 visibility=True, opacity=1.0, pickable=True):
        """
        Creates a new surface model.

        :param filename: path to vtk grid file.
        :param colour: (R,G,B) where each are floats [0-1]
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        :param pickable: boolean, True|False
        """
        super(VTKUnstructuredGridModel, self).__init__(colour, visibility,
                                                       opacity, pickable)

        self.source_file = None
        self.reader = None
        self.source = None
        self.cell_data_name = None
        self.threshold = None

        if filename is not None:

            vf.validate_is_file(filename)

            if filename.endswith(".vtk"):
                self.reader = vtk.vtkUnstructuredGridReader()

            elif filename.endswith(".vtu"):
                self.reader = vtk.vtkXMLUnstructuredGridReader()

            else:
                raise TypeError("File is not .vtu or .vtk extension")

            self.reader.SetFileName(filename)
            self.reader.Update()
            self.source = self.reader.GetOutput()

            self.source_file = filename
            self.name = os.path.basename(self.source_file)

        else:
            raise ValueError("Filename not specified")

        self.threshold = vtk.vtkThreshold()
        self.threshold.SetInputData(self.source)
        self.threshold.Update()
        self.thresholded_data = self.threshold.GetOutput()

        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputData(self.thresholded_data)
        self.mapper.Update()
        self.actor.SetMapper(self.mapper)

        self.cell_data_name = self.source.GetCellData().GetArrayName(0)

    def get_source_file(self):
        """
        Returns the filename that the model was loaded from, or
        empty string if the VTKSurfaceModel was not made from a file.

        :return:str filename
        """
        return self.source_file

    def get_cell_array(self) -> np.ndarray:
        """Return the cell data array as a numpy array

        :return: Cell data scalars
        :rtype: np.ndarray
        """
        cell_data = self.source.GetCellData()
        vtk_array = cell_data.GetArray(0)

        return numpy_support.vtk_to_numpy(vtk_array)

    def set_cell_array(self, data: np.ndarray):
        """Set the cell data in the grid.

        :param data: Numpy array of cell data points
        :type data: np.ndarray
        """

        vtk_array = numpy_support.numpy_to_vtk(data)
        vtk_array.SetName(self.cell_data_name)

        self.source.GetCellData().AddArray(vtk_array)

    def get_cell_array_bounds(self) -> Tuple[float, float]:
        """Return min/max values of cell array data.

        :return: Min, Max
        :rtype: float, float
        """
        cell_data = self.source.GetCellData()
        vtk_array = cell_data.GetArray(0)
        return vtk_array.GetRange()

    def threshold_between(self, lower: float, upper: float):
        """Set upper/lower limits to use for vtkThreshold

        :param lower: Lower limit
        :type lower: float
        :param upper: Upper limit
        :type upper: float
        """
        self.threshold.ThresholdBetween(lower, upper)
        self.threshold.Update()
