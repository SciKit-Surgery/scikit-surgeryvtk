# -*- coding: utf-8 -*-

"""
Module to load VTK surfaces using dictionary from ConfigurationManager.
"""

# pylint: disable=too-many-branches

import logging
import os
import vtk
import sksurgeryvtk.models.vtk_surface_model as sm

LOGGER = logging.getLogger(__name__)


class SurfaceModelLoader:
    """
    Class to load  VTK surface models and (optionally) associate them
    with vtkAssembly's. Surfaces should be defined in a .json file
    and loaded for example using sksurgerycore.ConfigurationManager.

    Surfaces have format:

    .. code-block::

        "surfaces": {
            "tumor": {

                "file": "path/to/model/tumor.vtk",
                "colour": [255, 0, 0],
                "opacity": 0.5,
                "visibility": true,
                "pickable": true,
                "toggleable": true,
                "texture": "path/to/texture/image.png",
                "outline": false
            }

    Assemblies have format:

    .. code-block::

        "assemblies": {
            "whole model": ["part1", "part2", "part3"]
        }

    """
    def __init__(self, data, directory_prefix=None):
        """
        Loads surface models and (optionally) assemblies from
        dictionary loaded by sksurgerycore.ConfigurationManager.

        :param data: data from sksurgerycore.ConfigurationManager
        :param prefix: directory name prefix as string
        """
        self.named_assemblies = {}
        self.named_surfaces = {}
        self.directory_prefix = directory_prefix

        if 'surfaces' in data.keys():
            surfaces = data['surfaces']
        else:
            raise KeyError("No 'surfaces' section defined in config")

        # Load surfaces
        for surface_name in surfaces:
            config = surfaces[surface_name]
            surface = self.__load_surface(config)
            surface.set_name(surface_name)
            self.named_surfaces[surface_name] = surface

        if 'assemblies' in data.keys():
            assemblies = data['assemblies']
            self.__check_assembly_duplicates(assemblies)

            # Iterate over assemblies
            for assembly in assemblies:
                logging.info("Adding assembly: %s", assembly)
                new_assembly = vtk.vtkAssembly()

                # Iterate over surfaces in this assembly
                for surface_name in assemblies[assembly]:
                    logging.info("Adding surface: %s to assembly: %s",
                                 surface_name, assembly)

                    # Check surface exists and add to assembly
                    if surface_name in self.named_surfaces:
                        surface = self.named_surfaces[surface_name]
                        new_assembly.AddPart(surface.actor)

                    else:
                        raise KeyError(f"Trying to add {surface_name} to \
                                vtkAssembly, but it is not a valid surface.")

                self.named_assemblies[assembly] = new_assembly

    def __load_surface(self, config):

        if 'file' in config.keys():
            file_name = config['file']
        else:
            raise KeyError("No 'file' section defined in config")

        if 'opacity' in config.keys():
            opacity = config['opacity']
        else:
            raise KeyError("No 'opacity' section defined in config")

        if 'visibility' in config.keys():
            visibility = config['visibility']
        else:
            raise KeyError("No 'visibility' section defined in config")

        if 'colour' in config.keys():
            colour = config['colour']
        else:
            raise KeyError("No 'colour' section defined in config")

        if 'pickable' in config.keys():
            pickable = config['pickable']
        else:
            raise KeyError("No 'pickable' section defined in config")

        outline = False
        if 'outline' in config.keys():
            outline = config['outline']

        colour_as_float = [colour[0] / 255.0,
                           colour[1] / 255.0,
                           colour[2] / 255.0
                           ]

        tmp_name = file_name
        if self.directory_prefix is not None:
            tmp_name = os.path.join(self.directory_prefix, tmp_name)

        model = sm.VTKSurfaceModel(tmp_name,
                                   colour_as_float,
                                   visibility,
                                   opacity,
                                   pickable,
                                   outline)

        if 'texture' in config.keys():
            texture_file = config['texture']
            if self.directory_prefix is not None:
                texture_file = os.path.join(self.directory_prefix, texture_file)
            model.set_texture(texture_file)

        if 'no shading' in config.keys():
            no_shading = config['no shading']
            model.set_no_shading(no_shading)

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

    def get_surface_models(self):
        """
        Convenience method, to get all models.

        Useful for unit testing for example.

        :return: list of VTKSurfaceModel
        """
        return self.named_surfaces.values()
