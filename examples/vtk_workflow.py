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
from sksurgeryoverlay.vtk import VTKOverlayWindow, VTKModel
from PySide2.QtWidgets import QApplication

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def main():
    app = QApplication([])

    # How many cameras are connected?
    num_cameras = count_cameras()

    wrapper = source_wrapper.VideoSourceWrapper()
    wrapper.save_timestamps = True

    vtk_overlay_windows = []
    camera_dims = (1280, 720)

    # Connect to all the cameras
    # and create a VTK overlay window for each one
    for camera_idx in range(num_cameras):
        wrapper.add_camera(camera_idx, camera_dims)
        vtk_overlay = VTKOverlayWindow.VTKOverlayWindow(wrapper, camera_idx)
        #vtk_overlay._RenderWindow.SetSize(camera_dims[0], camera_dims[1])

        vtk_overlay_windows.append(vtk_overlay)

    # Make all VTK windows use the same camera for the model layer
    # If the model is rotated/moved in one view, the others ones also change
    overlay_master_camera = vtk_overlay_windows[0].get_model_camera()
    for idx in range(1, num_cameras):
        vtk_overlay_windows[idx].link_foreground_cameras(overlay_master_camera)

    # Add VTK Models
    model_dir = './inputs/Liver'
    vtk_models = VTKModel.get_VTK_data(model_dir)
    
    for overlay in vtk_overlay_windows:
        overlay.update_background_renderer()  
        overlay.add_VTK_models(vtk_models)

    # Set up the output file writer
    filename = 'outputs/test.avi'
    writer = video_writer.OneSourcePerFileWriter(filename)
    writer.set_frame_source(wrapper)
    writer.create_video_writers()

    # Run
    n_frames = 100
    for i in range(n_frames):
        wrapper.get_next_frames()

        cv2.waitKey(1)

        for overlay in vtk_overlay_windows:
            overlay.update_background_renderer()

        writer.write_frame()

    writer.release_video_writers()
    writer.write_timestamps()

    
if __name__ == "__main__":
    main()
