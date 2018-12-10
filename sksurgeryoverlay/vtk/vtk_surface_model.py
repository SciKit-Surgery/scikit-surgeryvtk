#  -*- coding: utf-8 -*-

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
        self.source_file = filename
        self.reader = None
        self.source = None

        # Works like FactoryMethod. Could be refactored elsewhere.
        if filename is not None:

            if not vf.validate_is_file(filename):
                raise ValueError('Not a valid file: {}'.format(filename))

            if self.source_file.endswith('.vtk'):
                self.reader = vtk.vtkPolyDataReader()

            elif self.source_file.endswith('.stl'):
                self.reader = vtk.vtkSTLReader()

            elif self.source_file.endswith('.ply'):
                self.reader = vtk.vtkPLYReader()

            else:
                raise ValueError(
                    'File type not supported for model loading: {}'.format(
                        self.source_file))

            self.reader.SetFileName(self.source_file)
            self.reader.Update()
            self.source = self.reader.GetOutput()

        else:
            # Creates a new empty vtkPolyData, that the client
            # can dynamically fill with new data.
            self.source = vtk.vtkPolyData()

        # Setup rest of pipeline.
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputData(self.source)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.set_colour(colour)
        self.set_visibility(visibility)
        self.set_opacity(opacity)

    def set_colour(self, colour):
        """
        Set the colour of the model.

        :param colour: (R,G,B) where each are [0-1]
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
