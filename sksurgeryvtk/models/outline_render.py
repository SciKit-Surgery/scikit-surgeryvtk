"""
Uses vtkPolyDataSilhouette filter to create an outline actor
"""
from sksurgeryvtk.models.vtk_base_actor import VTKBaseActor
#from vtkmodules.vtkRenderingCore import vtkActor
#from vtkmodules.vtkFiltersHybrid import vtkPolyDataSilhouette
#from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper

class VTKOutlineActor(VTKBaseActor):
    """
    Class to handle requests to render an outline model
    """
    def __init__(self, colour, pickable=True):
        """
        Constructs a new VTKOutlineActor

        :param colour (R,G,B) where each are floats [0-1]
        """
        super().__init__(colour, visibility=True,
                opacity=1.0, pickable=pickable)
