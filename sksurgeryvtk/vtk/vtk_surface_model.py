# -*- coding: utf-8 -*-

"""
VTK pipeline to represent a surface model via a vtkPolyData.
"""

import os
import vtk
import sksurgerycore.utilities.validate_file as vf
import sksurgeryvtk.vtk.vtk_base_model as vbm

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

        # Setup rest of pipeline.
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.source)
        self.actor.SetMapper(self.mapper)
