# -*- coding: utf-8 -*-

"""
Module to load VTK surfaces using ConfigurationManager.
"""

import logging
import vtk
import sksurgeryvtk.models.vtk_surface_model as sm

LOGGER = logging.getLogger(__name__)


class SurfaceModelLoader:
    """
    Class to load  VTK surface models from a sksurgerycore.ConfigurationManager.
    """
    def __init__(self, configuration_manager):
        """
        Loads surface models from configuration_manager.

        :param configuration_manager: configuration_manager from sksurgerycore.
        """
        self.named_assemblies = {}
        self.named_surfaces = {}

        data = configuration_manager.get_copy()
        surfaces = data['surfaces']

        if surfaces is None:
            raise ValueError("No 'surfaces' section defined")

        for outer_name in surfaces:
            config = surfaces[outer_name]
            object_type = config['type']
            if object_type is None:
                raise ValueError('Invalid config, as type is required')
            if object_type == 'surface':
                surface = self.__load_surface(config)
                self.named_surfaces[outer_name] = surface
            elif object_type == 'assembly':
                assembly = vtk.vtkAssembly()
                for inner_name in config:
                    if inner_name != 'type':
                        inner_config = config[inner_name]
                        inner_type = inner_config['type']
                        if inner_type is None:
                            raise ValueError('Invalid config, \
                            as type is required')
                        if inner_type != 'surface':
                            raise ValueError("Invalid config, \
                            as type must be 'surface'")
                        surface = self.__load_surface(inner_config)
                        self.named_surfaces[inner_name] = surface
                        assembly.AddPart(surface.actor)
                self.named_assemblies[outer_name] = assembly
            else:
                raise ValueError("Type must be 'surface' or 'assembly'")

    @staticmethod
    def __load_surface(config):
        file_name = config['file']
        opacity = config['opacity']
        visibility = config['visibility']
        colour = config['colour']
        colour_as_float = [colour[0] / 255.0,
                           colour[1] / 255.0,
                           colour[2] / 255.0
                           ]
        model = sm.VTKSurfaceModel(file_name,
                                   colour_as_float,
                                   visibility,
                                   opacity)
        return model

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
