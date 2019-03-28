# -*- coding: utf-8 -*-

"""
Module to load VTK surfaces using ConfigurationManager.
"""

import logging
import vtk
import sksurgerycore.utilities.validate_file as vf
import sksurgeryvtk.models.vtk_surface_model as sm

LOGGER = logging.getLogger(__name__)


class SurfaceModelLoader:
    """
    Class to load all VTK surface models, using ConfigurationManager.
    """
    def __init__(self, ConfigurationManager):
        """
        Loads surface models from ConfigurationManager.

        :param ConfigurationManager: ConfigurationManager from sksurgerycore.
        """
        self.valid_extensions = ['.vtk', '.stl', '.ply', '.vtp']
        self.named_assemblies = {}
        self.named_surfaces = {}

        # extract dictionary of params from ConfigurationManager
        # look for section 'surfaces'
        #
        # Format, something like (I don't know json format that well):
        # surfaces
        #   assembly
        #     name
        #     surface
        #     surface
        #   surface
        #   surface
        #
        # where surface contains
        #   file name, string
        #   colour = [R,G,B] where each are floats [0-1]
        #   opacity = float [0-1]
        #   visibility = True/False

        # for each entry in surfaces
        #   if assembly
        #     create new vtkAssembly
        #     store name:vtkAssembly in self.named_assemblies
        #       load each surface
        #       store name:VTKSurfaceModel in self.named_surfaces
        #  if surface
        #     load surface
        #     store name:VTKSurfaceModel in self.named_surfaces

    def get_assembly(self, name):
        """
        Fetches a vtkAssembly using the name.
        :param name: name of the assembly, as string
        :return: vtkAssembly
        """
        return self.named_assemblies[name]

    def get_assembly_names(self):
        """
        Returns the set of valid assembly names.
        :return: keys from self.named_assemblies
        """
        return self.named_assemblies.keys()

    def get_surface_model(self, name):
        """
        Fetches a VTKSurfaceModel using the name.
        :param name: name of the model
        :return: VTKSurfaceModel
        """
        return self.named_surfaces[name]

    def get_surface_model_names(self):
        """
        Returns the set of valid model names.
        :return: keys from self.named_surfaces
        """
        return self.named_surfaces.keys()
