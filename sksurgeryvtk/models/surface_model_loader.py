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

        if 'surfaces' in data.keys():
            surfaces = data['surfaces']
        else:
            raise KeyError("No 'surfaces' section defined in config")

        for surface_name in surfaces:
            config = surfaces[surface_name]
            surface = self.__load_surface(config)
            self.named_surfaces[surface_name] = surface

        if 'assemblies' in  data.keys():
            assemblies = data['assemblies']
            self.__check_assembly_duplicates(assemblies)

            for assembly in assemblies:
                new_assembly = vtk.vtkAssembly()

                for surface_name in assemblies[assembly]:
                    if surface_name in self.named_surfaces.keys():
                        surface = self.named_surfaces[surface_name]
                        new_assembly.AddPart(surface.actor)

                    else:
                        raise KeyError("Trying to add {} to vtkAssembly, \
                            but it is not a valid surface.".\
                                format(surface_name))

                self.named_assemblies[assembly] = new_assembly

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

    @staticmethod
    def __check_assembly_duplicates(assemblies):
        """ Load the model names from all assemblies into a list,
        then convert it to a set. With no duplicates, the elements
        in the set should be the same as the elements in the list.
        """
        all_models = []

        for assembly in assemblies:
            all_models.extend(assemblies[assembly])

        unique_models = set(all_models)

        if len(all_models) != len(unique_models):
            raise ValueError("Assemblies do not contain unique elements.")


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
