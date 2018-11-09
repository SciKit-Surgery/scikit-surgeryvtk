### Having some odd problem with import paths, this solves it for now
### TODO: Fix this properly
import os, sys
sys.path.append(os.getcwd())
sys.path.append('../scikit-surgeryimage')
###

from sksurgeryoverlay.vtk import VTKOverlayWindow, VTKModel
from PySide2.QtWidgets import QApplication

from sksurgeryimage.acquire import VideoWriter, SourceWrapper

import cv2

import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def main():
    app = QApplication([])

    size = (1280, 720)
    wrapper = SourceWrapper.VideoSourceWrapper()
    wrapper.add_camera(0, size)
    wrapper.save_timestamps = True

    wrapper.get_next_frames()

    overlay = VTKOverlayWindow.VTKOverlayWindow(wrapper)
    #overlay._RenderWindow.SetSize(size[0], size[1])
    filename = 'outputs/test.avi'
    writer = VideoWriter.OneSourcePerFileWriter(filename)
    overlay.update_background_renderer()
    
    model_dir = './inputs/Kidney'
    vtk_models = VTKModel.get_VTK_data(model_dir)
    overlay.add_VTK_models(vtk_models)

    writer.set_frame_source(wrapper)
    writer.create_video_writers()

    n_frames = 100
    while n_frames > 0:

        wrapper.get_next_frames()

        cv2.waitKey(1)
        overlay.update_background_renderer()

        writer.write_frame()
        n_frames -= 1

    writer.release_video_writers()
    writer.write_timestamps()

    # # Constructor sets up the vtk environment
    # overlay = vtkOverlay()
    

    # source = SourceWrapper()

    # overlay.SetInput(source)
    
    # writer = VideoWriter()

    # writer.SetInput(writer)

    # while True:
    #     source.update()
    #     overlay.update()
    #     writer.update()
    
if __name__ == "__main__":
    main()
