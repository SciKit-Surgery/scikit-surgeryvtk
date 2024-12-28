# -*- coding: utf-8 -*-

"""
VTKBaseActor defines what a scikit-surgery 'VTK model' is.
"""

import vtk


class VTKBaseActor():
    """
    Base class to provide a definition of what a scikit-surgery 'VTK model' is.
    In scikit-surgery, a 'VTK Model' must contain a member variable called
    actor, that is-a vtkActor. This VTKBaseActor class adds setters and
    getters for the actor's colour, visibility, opacity and pickable property.

    It is possible for various VTK implementations / derived classes to ignore
    the colour property. For example a point set could store an RGB tuple for
    each point, so when rendered, the overall colour property is effectively
    ignored. However, the property has been kept at this base class level for
    simplicity.
    """
    def __init__(self, colour, visibility=True, opacity=1.0, pickable=True):
        """
        Constructs a new VTKBaseActor. This class contains a vtkActor as
        a member variable. So, this method initialises the vtkActor
        with the properties provided as constructor arguments.

        :param colour: (R,G,B) where each are floats [0-1]
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        :param pickable: boolean, True|False
        """
        self.actor = vtk.vtkActor()
        self.set_colour(colour)
        self.set_visibility(visibility)
        self.set_opacity(opacity)
        self.set_pickable(pickable)

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

    def get_opacity(self):
        """
        Returns float [0-1].
        """
        return self.actor.GetProperty().GetOpacity()

    def set_visibility(self, visibility):
        """
        Sets the visibility.

        :param visibility: [True|False]
        :raises: TypeError if not a boolean
        """
        if not isinstance(visibility, bool):
            raise TypeError('Visibility should be True or False')

        self.actor.SetVisibility(visibility)

    def get_visibility(self):
        """
        Returns bool, True if Actor is visible and False otherwise.
        :return: bool
        """
        return bool(self.actor.GetVisibility())

    def toggle_visibility(self):
        """
        Toggles model visbility on/off.
        """

        if self.actor.GetVisibility():
            self.actor.VisibilityOff()

        else:
            self.actor.VisibilityOn()

    def get_pickable(self):
        """
        Returns the pickable flag.
        """
        return self.actor.GetPickable()

    def set_pickable(self, pickable):
        """
        Enables the user to set the pickable flag.

        :param pickable:
        :raises: TypeError if not a boolean
        """
        if not isinstance(pickable, bool):
            raise TypeError('Pickable should be True or False')

        self.actor.SetPickable(pickable)
