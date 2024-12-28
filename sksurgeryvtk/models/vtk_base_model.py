# -*- coding: utf-8 -*-

"""
VTKBaseModel defines what a scikit-surgery 'VTK model' is, augmenting
VTKBaseActor by adding an optional outline actor member variable.
"""

import sksurgeryvtk.utils.matrix_utils as mu
from sksurgeryvtk.models.vtk_base_actor import VTKBaseActor
from sksurgeryvtk.models.outline_render import VTKOutlineActor


class VTKBaseModel(VTKBaseActor):
    """
    Defines a base class for 'VTK Models' which are objects that
    contain at least one vtkActor. From v1.1 we can optionally
    contain an additional outline rendering vtkActor.

    See also: VTKBaseActor parent class.
    """
    def __init__(self, colour, visibility=True, opacity=1.0, pickable=True,
            outline=False):
        """
        Constructs a new VTKBaseModel with self.name = None.

        :param colour: (R,G,B) where each are floats [0-1]
        :param visibility: boolean, True|False
        :param opacity: float [0,1]
        :param pickable: boolean, True|False
        :param outline: boolean, if true the outline of the actor is shown.
        """
        super().__init__(colour, visibility, opacity, pickable)

        self.name = None
        self.outline_actor = None
        self.set_outline(outline)

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

    def get_outline(self):
        """
        Returns the outline flag.
        """
        if self.outline_actor is None:
            return False

        return True

    def set_outline(self, outline):
        """
        Enables the user to set the outline rendering flag.

        :param outline:
        :raises: TypeError if not a boolean
        """
        if not isinstance(outline, bool):
            raise TypeError('outline should be True or False')

        if outline:
            if self.outline_actor is None:
                self.outline_actor = VTKOutlineActor(self.get_colour(),
                        bool(self.get_pickable()))
        else:
            if self.outline_actor is not None:
                self.outline_actor = None

    def get_outline_actor(self, active_camera):
        """
        Sets up the outline renderer. and returns the
        outline actor so you can add it to your renderer
        Before doing this self.actor
        should have been set up with a mapper and we need a camera
        to know where we're projecting from.

        :param active_camera: the vtk camera.
            Use vtk_overlay.foreground_renderer.GetActiveCamera()

        :returns the outline actor
        """
        if self.get_outline():
            self.outline_actor.initialise(active_camera, self.actor)
            return self.outline_actor.actor

        return None
