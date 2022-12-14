"""
Uses vtkPolyDataSilhouette filter to create an outline actor
"""
import vtk
#from vtkmodules.vtkRenderingCore import vtkActor
#from vtkmodules.vtkFiltersHybrid import vtkPolyDataSilhouette
#from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper

class VTKOutlineActor():
    """
    Class to handle requests to render an outline model
    """
    def __init__(self, colour, pickable=True):
        """
        Constructs a new VTKOutlineActor

        :param colour (R,G,B) where each are floats [0-1]
        """

        self.actor = vtk.vtkActor()
        self.set_colour(colour)
        self.set_pickable(pickable)

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
