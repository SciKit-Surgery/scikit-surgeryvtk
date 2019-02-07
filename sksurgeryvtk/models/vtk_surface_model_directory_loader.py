# -*- coding: utf-8 -*-

"""
Module to load VTK surfaces.
"""

import os
import csv
import logging
from vtk.util import colors
import sksurgerycore.utilities.validate_file as vf
import sksurgeryvtk.models.vtk_surface_model as sm

LOGGER = logging.getLogger(__name__)


class VTKSurfaceModelDirectoryLoader:
    """
    Class to load all VTK surface models in a directory.
    Given a directory name, will also load colours from
    a file called colours.txt.
    """
    def __init__(self, directory_name):
        """
        Loads surface models from a given directory.

        :param directory_name: string, directory name.
        :raises: ValueError if directory_name is unreadable.
        """
        self.colours = None
        self.files = []
        self.models = []
        self.valid_extensions = ['.vtk', '.stl', '.ply', '.vtp']
        self.get_models(directory_name)

    def get_models(self, directory_name):
        """
        Loads models from the given directory.

        :param directory_name: string, readable directory name.
        :raises: TypeError, ValueError, RuntimeError
        """
        if directory_name is None:
            raise ValueError('Directory name is None')
        if not directory_name:
            raise ValueError('Directory name is empty')
        if not os.path.exists(directory_name):
            raise ValueError('Directory does not exist: {}'
                             .format(directory_name))
        if not os.access(directory_name, os.X_OK):
            raise ValueError('Directory is not executable: {}'
                             .format(directory_name))
        if not os.access(directory_name, os.R_OK):
            raise ValueError('Directory is not readable: {}'
                             .format(directory_name))

        # Reset
        self.files = []
        self.models = []

        # Load colours if they exist.
        self.get_model_colours(directory_name)

        # Will this do for now?
        if len(self.colours) < len(self.models):
            raise ValueError('Not enough colours')

        # This may well throw FileNotFoundError which is fine.
        # If its not valid I want the Exception raised.
        LOGGER.info("Loading models from %s", directory_name)
        self.files = os.listdir(directory_name)

        # Loop through each file, trying to load it.
        counter = 0

        for filename in self.files:

            full_path = os.path.join(directory_name, filename)

            if self.is_valid_model_file(full_path):

                LOGGER.info("Loading model from %s", full_path)

                if filename in self.colours:
                    model_colour = self.colours[filename]
                else:
                    model_colour = self.colours[str(counter)]

                model = sm.VTKSurfaceModel(full_path, model_colour)
                model.set_name(filename)
                self.models.append(model)

                LOGGER.info("Loaded model from %s", full_path)
                counter += 1

        if not self.models:
            LOGGER.info("No model files in given directory")

    def is_valid_model_file(self, file):
        """
        Check if the passed file is a valid model file by
        checking the extension.
        """
        vf.validate_is_file(file)

        _, extension = os.path.splitext(file)
        if extension in self.valid_extensions:
            return True

        return False

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
            with open(colour_file, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                counter = 0
                for row in csv_reader:
                    if len(row) != 4:
                        raise ValueError('Line '
                                         + str(counter)
                                         + ' does not contain '
                                         + 'name and 3 numbers')
                    self.colours[str(row[0])] = (float(row[1]),
                                                 float(row[2]),
                                                 float(row[3]))
        else:
            for i in range(len(default_colours)):
                self.colours[str(i)] = default_colours[i]
