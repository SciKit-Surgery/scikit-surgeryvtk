# coding=utf-8

""" Demo app, to render a model from a particular perspective"""
import numpy as np
import sys
import vtk
from PySide2 import QtWidgets
from sksurgeryvtk.vtk import vtk_overlay_window, vtk_surface_model_directory_loader
import sksurgeryvtk.camera.vtk_camera_model as cam

import csv
import cv2

def run_demo(image_file, width, height, model_dir, extrinsics_file, intrinsics_file):

    app = QtWidgets.QApplication([])

    if image_file:
        img = cv2.imread(image_file)
        height, width = img.shape[:2]
    
    
    window = vtk_overlay_window.VTKOverlayWindow()
    window.set_video_image(img)
    window.show()
    window.GetRenderWindow().SetSize(width, height)
    print("  Width:" + str(width))
    print("  Height:" + str(height))

    if model_dir:
        print("  Model directory: " + str(model_dir))
        model_loader = vtk_surface_model_directory_loader.VTKSurfaceModelDirectoryLoader(model_dir)
        window.add_vtk_models(model_loader.models)

    if extrinsics_file and intrinsics_file:
        
        # Load intrinsics for projection matrix.
        intrinsics = np.loadtxt(intrinsics_file)

        # Load extrinsics for camera pose (position, orientation).
        extrinsics = np.loadtxt(extrinsics_file)
        model_to_camera = cam.create_vtk_matrix_from_numpy(extrinsics)

        # OpenCV maps from chessboard to camera.
        # Assume chessboard == world, so the input matrix is world_to_camera.
        # We need camera_to_world to position the camera in world coordinates.
        # So, invert it.
        model_to_camera.Invert()

        projection_matrix = cam.compute_projection_matrix(width, height,
                                                        float(intrinsics[0][0]), float(intrinsics[1][1]),
                                                        float(intrinsics[0][2]), float(intrinsics[1][2]),
                                                        0.01, 1000,
                                                        1
                                                        )
        camera = window.get_foreground_camera()
        cam.set_camera_pose(camera, model_to_camera)
        cam.set_projection_matrix(camera, projection_matrix)

    return sys.exit(app.exec_())
