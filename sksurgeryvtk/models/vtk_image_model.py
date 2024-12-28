# -*- coding: utf-8 -*-

"""
VTKImageModel creates a VTK pipeline to represent an image with a vtkImageActor.
"""

# pylint:disable=super-with-arguments

import os
import vtk
import sksurgeryvtk.models.vtk_base_model as vbm


class VTKImageModel(vbm.VTKBaseModel):
    """
    Class to represent a VTK image model. Normally
    read from a file, but could be created on the fly.
    """
    def __init__(self, filename, visibility=True, opacity=1.0):
        """
        Creates an image model, represented as a vtkImageActor.

        :param filename: filename, should be .png in the first instance.
        :param visibility: [True/False] boolean
        :param opacity: [0, 1]
        """
        super(VTKImageModel, self).__init__((1.0, 1.0, 1.0),
                                            visibility,
                                            opacity
                                           )

        self.source_file = None
        self.reader = None
        self.source = None

        if filename is not None:
            self.reader = vtk.vtkPNGReader()
            self.reader.SetFileName(filename)
            self.reader.Update()
            self.source = self.reader.GetOutput()
            self.source_file = filename
            self.name = os.path.basename(self.source_file)
        else:
            self.source = vtk.vtkImageData()
            self.name = ""

        self.actor = vtk.vtkImageActor()
        self.actor.SetInputData(self.source)
