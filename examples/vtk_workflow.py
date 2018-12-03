### Having some odd problem with import paths, this solves it for now
### TODO: Fix this properly
import os, sys
sys.path.append(os.getcwd())
sys.path.append('../scikit-surgeryimage')
###
import logging
import cv2

from sksurgeryimage.acquire import video_writer, source_wrapper
from sksurgeryimage.utilities.camera_utilities import count_cameras
from sksurgeryoverlay.vtk import vtk_overlay_window, vtk_model
from PySide2.QtWidgets import QApplication, QWidget

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class BasicOverlayDemo():

    def __init__(self):

        self.wrapper = source_wrapper.VideoSourceWrapper()
        self.wrapper.save_timestamps = True

        self.vtk_overlay_windows = []
        
        self.create_overlay_for_all_cameras()
        self.synchronise_vtk_cameras()

    
    def create_overlay_for_all_cameras(self):
        """
        Create an overlay window for each camera
        that is connected.
        """
        self.num_cameras = count_cameras()
        camera_dims = (1280, 720)

        for camera_idx in range(self.num_cameras):
            self.wrapper.add_camera(camera_idx, camera_dims)
            vtk_overlay = vtk_overlay_window.VTKOverlayWindow(self.wrapper.sources[camera_idx])
            self.vtk_overlay_windows.append(vtk_overlay)

    def add_vtk_models_to_scene(self, model_dir):
        """
        Add VTK Models to scene.
        """
        model_loader = vtk_model.LoadVTKModelsFromDirectory()
        vtk_models = model_loader.get_models(model_dir)
        
        for overlay in self.vtk_overlay_windows:
            overlay.update_background_renderer()  
            overlay.add_VTK_actors_to_foreground(vtk_models)

    def synchronise_vtk_cameras(self):
        """
        Make all VTK windows use the same camera for the model layer
        If the model is rotated/moved in one view, the others ones also change.
        """
        overlay_master_camera = self.vtk_overlay_windows[0].get_model_camera()
        for idx in range(1, self.num_cameras):
            self.vtk_overlay_windows[idx].link_foreground_cameras(overlay_master_camera)

    def setup_output_file_writer(self, filename):
        """
        Set up the output file writer.
        """
        self.writer = video_writer.OneSourcePerFileWriter(filename)
        self.writer.set_frame_source(self.wrapper)
        self.writer.create_video_writers()

    def run(self, num_frames_to_capture):
        for i in range(num_frames_to_capture):
            self.wrapper.get_next_frames()

            cv2.waitKey(1)

            for overlay in self.vtk_overlay_windows:
                overlay.update_background_renderer()

            self.writer.write_frame()

        self.writer.release_video_writers()
        self.writer.write_timestamps()

def main():

    app = QApplication([])

    demo = BasicOverlayDemo()
    

    model_dir = 'inputs/Liver'
    output_file = 'outputs/test.avi'

    demo.add_vtk_models_to_scene( model_dir)
    demo.setup_output_file_writer(output_file)

    num_frames = 100
    demo.run(num_frames)

    
if __name__ == "__main__":
    main()
