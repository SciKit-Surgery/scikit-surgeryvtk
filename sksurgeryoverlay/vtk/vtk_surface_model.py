#  -*- coding: utf-8 -*-

"""
VTK pipeline to represent surfaces.
"""

import os
import vtk
import sksurgerycore.utilities.validate_file as vf


class VTKSurfaceModel:
    """
    Class to represent a VTK poly data. Normally
    read from a file, but could be created on the fly.
    """
    def __init__(self, filename, colour, visibility=True, opacity=1.0):
        """
        Creates a new vtkPolyData model.
        """
        self.source_file = None
        self.name = None
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
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputData(self.source)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.set_colour(colour)
        self.set_visibility(visibility)
        self.set_opacity(opacity)

    def get_name(self):
        """
        Returns the name of the model. If the model was
        created from file, it will be the basename of the
        full filepath. If it was created without a file
        name, then it will be an empty string, or whatever
        the user has programmatically set the name to.

        :return: str, the name
        """
        return self.name

    def set_name(self, name):
        """
        Sets the name.

        :param name: str containing a name
        :raises: TypeError if not string, ValueError if empty
        """
        if not isinstance(name, str):
            raise TypeError('The name should be a string')
        if not name:
            raise ValueError('Name should not be an empty string')

        self.name = name

    def get_colour(self):
        """
        Returns the current colour of the surface model.

        :return: R, G, B where each are floats [0-1]
        """
        return self.actor.GetProperty().GetColor()

    def set_colour(self, colour):
        """
        Set the colour of the model.

        :param colour: (R,G,B) where each are floats [0-1]
        :raises TypeError if R,G,B not float, ValueError if outside range.
        """
        red, green, blue = colour
        if not isinstance(red, float):
            raise TypeError('Red component should be float [0-1]')
        if not isinstance(green, float):
            raise TypeError('Green component should be float [0-1]')
        if not isinstance(blue, float):
            raise TypeError('Blue component should be float [0-1]')
        if red < 0 or red > 1:
            raise ValueError('Red component should be [0-1]')
        if green < 0 or green > 1:
            raise ValueError('Green component should be [0-1]')
        if blue < 0 or blue > 1:
            raise ValueError('Blue component should be [0-1]')

        self.actor.GetProperty().SetColor(colour)

    def set_opacity(self, opacity):
        """
        Set the opacity.

        :param opacity: [0-1] float between 0 and 1.
        :raises: TypeError if not a float, ValueError if outside range.
        """
        if not isinstance(opacity, float):
            raise TypeError('Opacity should be a float [0-1]')
        if opacity < 0 or opacity > 1:
            raise ValueError('Opacity should be [0-1]')

        self.actor.GetProperty().SetOpacity(opacity)

    def set_visibility(self, visibility):
        """
        Sets the visibility.

        :param visibility: [True|False]
        :raises: TypeError if not a boolean
        """
        if not isinstance(visibility, bool):
            raise TypeError('Visibility should be True or False')

        self.actor.SetVisibility(visibility)
