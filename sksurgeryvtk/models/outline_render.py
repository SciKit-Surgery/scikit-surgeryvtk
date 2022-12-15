"""
Uses vtkPolyDataSilhouette filter to create an outline actor
"""
import vtk
from sksurgeryvtk.models.vtk_base_actor import VTKBaseActor
#from vtkmodules.vtkFiltersHybrid import vtkPolyDataSilhouette
#from vtkmodules.vtkRenderingCore import vtkPolyDataMapper

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

    def initialise(self, active_camera, actor):
        """
        Call this after you have set up an actor, mapper,
        and camera to create an outline rendering

        :param active_camera: a vtk camera so we know from what perspective to
            create the silhouette, use
            vtk_overlay.foreground_renderer.GetActiveCamera()
        :param actor: the vtk actor we're silhoutting.

        """
        silhouette = vtk.vtkPolyDataSilhouette()
        silhouette.SetEnableFeatureAngle(False)

        silhouette.SetCamera(active_camera)
        silhouette.SetInputData(actor.GetMapper().GetInput())

        silhouette_mapper = vtk.vtkPolyDataMapper()
        silhouette_mapper.SetInputConnection(silhouette.GetOutputPort())

        self.actor.SetMapper(silhouette_mapper)
        self.actor.GetProperty().SetLineWidth(5)
