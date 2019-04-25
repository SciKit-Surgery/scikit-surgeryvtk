# -*- coding: utf-8 -*-

"""
Base class to provide a base class definition of what a 'VTK model' is.
In the context of this project, at this current moment in time,
its an object that has a member variable called 'actor' that is a vtkActor.
"""

import vtk
import sksurgeryvtk.utils.matrix_utils as mu


class VTKBaseModel():
    """
    Defines a base class for 'VTK Models' which are objects that
    contain a vtkActor. This class enables you to set the colour,
    visibility and opacity. Note that this colour property is set on the actor.
    It is possible for various VTK implementations to ignore this.
    For example a point set could store an RGB tuple for each point,
    so when rendered, the overall colour property is effectively ignored.
    However, the property has been kept at this base class level for simplicity.
    """
    def __init__(self, colour, visibility=True, opacity=1.0, pickable=True):
        """
        Constructs a new VTKBaseModel with self.name = None.

        :param colour: (R,G,B) where each are floats [0-1]
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        :param pickable: boolean, True|False
        """
        self.name = None
        self.actor = vtk.vtkActor()
        self.set_visibility(visibility)
        self.set_opacity(opacity)
        self.set_colour(colour)
        self.set_pickable(pickable)

    def get_name(self):
        """
        Returns the name of the model.

        :return: str, the name, which can be None if not yet set.
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
        Returns the current colour of the model.

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

    def toggle_visibility(self):
        """
        Toggles model visbility on/off.
        """

        if self.actor.GetVisibility():
            self.actor.VisibilityOff()

        else:
            self.actor.VisibilityOn()

    def set_user_matrix(self, matrix):
        """
        Sets the vtkActor UserMatrix. This simply tells the
        graphics pipeline to move/translate/rotate the actor.
        It does not transform the original data.

        :param matrix: vtkMatrix4x4
        """
        mu.validate_vtk_matrix_4x4(matrix)
        self.actor.SetUserMatrix(matrix)

    def get_user_matrix(self):
        """
        Getter for vtkActor UserMatrix.
        :return: vtkMatrix4x4
        """
        return self.actor.GetUserMatrix()

    def set_pickable(self, pickable):
        """
        Enables the user to set the pickable flag.

        :param pickable:
        :raises: TypeError if not a boolean
        """
        if not isinstance(pickable, bool):
            raise TypeError('Pickable should be True or False')

        self.actor.SetPickable(pickable)
