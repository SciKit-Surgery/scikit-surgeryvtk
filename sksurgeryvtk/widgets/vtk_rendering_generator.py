# -*- coding: utf-8 -*-

"""
Module to provide a basic VTK render window for test data generation.
"""

# pylint: disable=too-many-instance-attributes,
# pylint: disable=no-name-in-module, too-many-arguments

import os
import numpy as np
import cv2
from PySide6 import QtWidgets
import sksurgerycore.utilities.file_utilities as fu
import sksurgerycore.configuration.configuration_manager as config
import sksurgeryvtk.widgets.vtk_overlay_window as vo
import sksurgeryvtk.models.surface_model_loader as sl
import sksurgeryvtk.camera.vtk_camera_model as cm
import sksurgeryvtk.utils.matrix_utils as mu


class VTKRenderingGenerator(QtWidgets.QWidget):
    """
    Class contains a VTKOverlayWindow and a few extra functions to
    facilitate rendering loops for generating test data.

    :param models_file: JSON file describing VTK models, in SNAPPY format
    :param background_image: RGB image to render in background
    :param intrinsic_file: [3x3] matrix in text file, in numpy format
    :param camera_to_world: list of [rx,ry,rz,tx,ty,tz] in degrees/millimetres
    :param left_to_right: list of [rx,ry,rz,tx,ty,tz] in degrees/millimetres
    :param offscreen: if true, renders offscreen
    :param zbuffer: if true, causes VTK to render just the z-buffer
    :param gaussian_sigma: if non-zero, adds blurring to the rendered image
    :param gaussian_window_size: window size of OpenCV Gaussian kernel
    :param clipping_range: VTK clipping range (near, far)
    :param init_widget: If True we will call self.Initialize and self.Start
        as part of the init function. Set to false if you're on Linux.
    """
    def __init__(self,
                 models_file,
                 background_image,
                 intrinsic_file,
                 camera_to_world=None,
                 left_to_right=None,
                 offscreen=False,
                 zbuffer=False,
                 gaussian_sigma=0.0,
                 gaussian_window_size=11,
                 clipping_range=(1, 1000),
                 init_widget=True
                 ):
        super().__init__()
        self.gaussian_sigma = gaussian_sigma
        self.gaussian_window_size = gaussian_window_size

        self.img = cv2.imread(background_image)

        self.configuration_manager = config.ConfigurationManager(models_file)
        self.configuration_data = self.configuration_manager.get_copy()

        file = fu.get_absolute_path_of_file(models_file)
        dirname = os.path.dirname(file)

        self.model_loader = sl.SurfaceModelLoader(self.configuration_data,
                                                  dirname
                                                  )

        self.window_container = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self.window_container)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.overlay = vo.VTKOverlayWindow(offscreen=offscreen,
                                           zbuffer=zbuffer,
                                           init_widget=init_widget)
        self.overlay.set_video_image(self.img)
        self.overlay.add_vtk_models(self.model_loader.get_surface_models())
        self.clip_near = clipping_range[0]
        self.clip_far = clipping_range[1]

        self.intrinsics = np.loadtxt(intrinsic_file, dtype=float)
        self.setup_intrinsics()

        self.left_camera_to_world = np.eye(4)
        self.camera_to_world = np.eye(4)
        self.left_to_right = np.eye(4)
        self.setup_camera_extrinsics(camera_to_world, left_to_right)

        self.layout.addWidget(self.overlay)
        # self.overlay.show()
        self.overlay.Initialize()
        # self.overlay.Start()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.overlay.Finalize()

    def set_clipping_range(self, minimum, maximum):
        """
        Sets the clipping range on the foreground camera.

        :param minimum: minimum in millimetres
        :param maximum: maximum in millimetres
        """
        self.clip_near = minimum
        self.clip_far = maximum
        self.overlay.get_foreground_camera().SetClippingRange(minimum, maximum)

    def set_smoothing(self, sigma, window_size):
        """
        Sets the Gaussian blur.

        :param sigma: standard deviation of Gaussian function.
        :param window_size: sets the window size of Gaussian kernel (pixels).
        """
        self.gaussian_sigma = sigma
        self.gaussian_window_size = window_size

    def setup_intrinsics(self):
        """
        Set the intrinsics of the foreground vtkCamera.
        """
        f_x = self.intrinsics[0, 0]
        c_x = self.intrinsics[0, 2]
        f_y = self.intrinsics[1, 1]
        c_y = self.intrinsics[1, 2]
        width, height = self.img.shape[1], self.img.shape[0]

        cm.set_camera_intrinsics(self.overlay.get_foreground_renderer(),
                                 self.overlay.get_foreground_camera(),
                                 width,
                                 height,
                                 f_x,
                                 f_y,
                                 c_x,
                                 c_y,
                                 self.clip_near,
                                 self.clip_far)

    def setup_camera_extrinsics(self,
                                camera_to_world,
                                left_to_right=None
                                ):
        """
        Decomposes parameter strings into 6DOF
        parameters, and sets up camera-to-world and left_to_right for stereo.

        :param camera_to_world: list of [rx,ry,rz,tx,ty,tz] in degrees/mm
        :param left_to_right: list of [rx,ry,rz,tx,ty,tz] in degrees/mm
        """
        if camera_to_world is not None:
            self.left_camera_to_world = mu.create_matrix_from_list(
                camera_to_world)
        if left_to_right is not None:
            self.left_to_right = mu.create_matrix_from_list(left_to_right)
        self.camera_to_world = cm.compute_right_camera_pose(
            self.left_camera_to_world,
            self.left_to_right)
        self.overlay.set_camera_pose(self.camera_to_world)

    def set_all_model_to_world(self, model_to_world):
        """
        Decomposes the model_to_world string into rx,ry,rx,tx,ty,rz,
        constructs a 4x4 matrix, and applies it to all models.

        :param model_to_world: [4x4] numpy ndarray, rigid transform
        """
        if model_to_world is not None:
            m2w = mu.create_matrix_from_list(model_to_world)
            vtk_matrix = mu.create_vtk_matrix_from_numpy(m2w)
            for model in self.model_loader.get_surface_models():
                model.set_user_matrix(vtk_matrix)

    def set_model_to_worlds(self, dict_of_transforms):
        """
        Given a dictionary of transforms, will iterate by name,
        and apply the transform to the named object.
        :param dict_of_transforms: {name, [rx, ry, rz, tx, ty, tz]}
        """
        if dict_of_transforms is not None:
            for name in dict_of_transforms:
                if name in self.model_loader.get_surface_model_names():
                    model = self.model_loader.get_surface_model(name)
                    m2w = mu.create_matrix_from_list(dict_of_transforms[name])
                    vtk_matrix = mu.create_vtk_matrix_from_numpy(m2w)
                    model.set_user_matrix(vtk_matrix)
                else:
                    raise ValueError("'" + name + "' is not in set of models.")

    def get_image(self):
        """
        Returns the rendered image, with post processing like smoothing.
        :return: numpy ndarray representing rendered image (RGB)
        """
        self.overlay.Render()
        self.repaint()
        img = self.overlay.convert_scene_to_numpy_array()
        smoothed = img
        if self.gaussian_sigma > 0:
            smoothed = cv2.GaussianBlur(img,
                                        (self.gaussian_window_size,
                                         self.gaussian_window_size),
                                        self.gaussian_sigma)
        return smoothed

    def get_masks(self):
        """
        If we want to render masks for test data for DL models for instance,
        we typically want distinct masks per model object. This method
        returns a dictionary of new images corresponding to each named model.

        If model is shaded, the shading is turned off to get masks,
        the masks are acquired, and the shading is applied again.

        Note: You should ensure self.gaussian_sigma == 0 (the default),
        and in the .json file.
        """
        result = {}
        # Check shading of models.
        models = self.model_loader.get_surface_models()
        shaded_models = [] # To track which ones were shaded.
        for model in models:
            if not model.no_shading:
                # Shading is active, deactivate it
                model.set_no_shading(True)
                shaded_models.append(True)
            else:
                shaded_models.append(False)

        # Should not be shaded.
        img = self.get_image()
        for index, model in enumerate(models):
            name = model.get_name()
            colour = (np.asarray(model.get_colour()) * 255).astype(np.uint8)
            mask = cv2.inRange(img, colour, colour)
            result[name] = mask
            # Use shaded_models list to reactivate shading to original setting.
            if shaded_models[index]:
                model.set_no_shading(False)

        return result
