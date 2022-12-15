# -*- coding: utf-8 -*-

"""
Module to load VTK surfaces.
"""

import os
import csv
import logging
from vtk.util import colors
import sksurgerycore.configuration.configuration_manager as cm
import sksurgeryvtk.models.vtk_surface_model as sm

LOGGER = logging.getLogger(__name__)


class VTKSurfaceModelDirectoryLoader:
    """
    Class to load all VTK surface models in a directory.
    """
    def __init__(self, directory_name, defaults_file=None):
        """
        Constructor loads surface models from a given directory.

        If a defaults_file is given, will match filename to a key in
        the defaults file, and set defaults, e.g. tumor.vtk matched to:

            "tumor": {
                "colour": [1.0, 0, 0],
                "opacity": 0.5,
                "visibility": true,
                "pickable": true,
                "toggleable": true,
                "texture": "path/to/texture/image.png",
                "outline": false
            }

        Alternatively, if a defaults_file is not present, a file called
        colours.txt can be used to specify colours for each file.

        If that's not present, then colours are just picked in order from
        an in-built list.

        defaults_file takes precedence over colours.txt if both present.

        :param directory_name: string, directory name.
        :param defaults_file: filename of json file with default settings
        :raises: ValueError if directory_name is unreadable.
        """
        if directory_name is None:
            raise ValueError('Directory name is None')
        if not directory_name:
            raise ValueError('Directory name is empty')
        if not os.path.exists(directory_name):
            raise ValueError(f'Directory does not exist: {directory_name}')
        if not os.access(directory_name, os.X_OK):
            raise ValueError(f'Directory is not executable: {directory_name}')
        if not os.access(directory_name, os.R_OK):
            raise ValueError(f'Directory is not readable: {directory_name}')

        self.configuration_data = None

        self.defaults_file = defaults_file
        if self.defaults_file:
            configuration_manager = cm.ConfigurationManager(self.defaults_file)
            self.configuration_data = configuration_manager.get_copy()

        self.colours = None
        if directory_name:
            self.get_model_colours(directory_name)

        self.models = []
        self.get_models(directory_name)

    # pylint: disable=too-many-branches
    def get_models(self, directory_name):
        """
        Loads models from the given directory.

        :param directory_name: string, readable directory name.
        :raises: TypeError, ValueError, RuntimeError
        """
        LOGGER.info("Loading models from %s", directory_name)

        # Reset
        files = []
        self.models = []

        # This may well throw FileNotFoundError which is fine.
        # If its not valid I want the Exception raised.
        files = os.listdir(directory_name)
        files.sort()

        # Loop through each file, trying to load it.
        counter = 0

        for filename in files:

            full_path = os.path.join(directory_name, filename)

            try:
                model = sm.VTKSurfaceModel(full_path, (1.0, 1.0, 1.0))
                model_name = os.path.splitext(model.get_name())[0]
                model.set_name(model_name)

                # New behaviour, if we provide defaults in a file, use them.
                if self.configuration_data:
                    if model_name in self.configuration_data.keys():
                        model_defaults = self.configuration_data[model_name]

                        if 'opacity' in model_defaults.keys():
                            opacity = model_defaults['opacity']
                            model.set_opacity(opacity)

                        if 'visibility' in model_defaults.keys():
                            visibility = model_defaults['visibility']
                            model.set_visibility(visibility)

                        if 'colour' in model_defaults.keys():
                            colour = model_defaults['colour']
                            colour_as_float = [colour[0] / 255.0,
                                               colour[1] / 255.0,
                                               colour[2] / 255.0
                                               ]
                            model.set_colour(colour_as_float)

                        if 'pickable' in model_defaults.keys():
                            pickable = model_defaults['pickable']
                            model.set_pickable(pickable)

                        if 'outline' in model_defaults.keys():
                            outline = model_defaults['outline']
                            model.set_outline(outline)

                        if 'texture' in model_defaults.keys():
                            texture_file = model_defaults['texture']
                            texture_file_path = os.path.join(directory_name,
                                                             texture_file)
                            model.set_texture(texture_file_path)

                        if 'no shading' in model_defaults.keys():
                            no_shading = model_defaults['no shading']
                            model.set_no_shading(no_shading)

                else:
                    # Original behaviour (see previous version in git)
                    # Either load colour from file, or we just pick a
                    # colour based on an index.
                    if filename in self.colours:
                        model_colour = self.colours[filename]
                    else:
                        LOGGER.info(
                            "Filename %s not found in colours.txt", filename)
                        model_colour = self.colours[str(counter)]
                    model.set_colour(model_colour)

                # Finally, add to list, increment counter.
                self.models.append(model)
                LOGGER.info("Loaded model from %s", full_path)
                counter += 1

            except ValueError:
                # Presume wrong type of file.
                LOGGER.info("Didn't load vtk_surface_model: %s", full_path)

        if not self.models:
            LOGGER.info("No valid model files in given directory")

        LOGGER.info("Loaded models from %s", directory_name)

    def get_model_colours(self, directory):
        """
        Load colours for each model from a .txt file in the model
        directory.
        """
        # pylint: disable=consider-using-enumerate

        self.colours = {}

        default_colours = [colors.red, colors.blue, colors.green,
                           colors.black, colors.white, colors.yellow,
                           colors.brown, colors.grey, colors.purple,
                           colors.pink]

        colour_file = directory + '/colours.txt'

        if os.path.exists(colour_file):
            with open(colour_file, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                counter = 0
                for row in csv_reader:
                    if len(row) != 4:
                        raise ValueError('Line '
                                         + str(counter)
                                         + ' does not contain '
                                         + 'name and 3 numbers')

                    filename = str(row[0])
                    full_path = os.path.join(directory, filename)
                    if not os.path.exists(full_path):
                        raise FileNotFoundError(
                                f"File {full_path} doesn't exist")

                    self.colours[filename] = (float(row[1]),
                                              float(row[2]),
                                              float(row[3]))
        else:
            for i in range(len(default_colours)):
                self.colours[str(i)] = default_colours[i]
