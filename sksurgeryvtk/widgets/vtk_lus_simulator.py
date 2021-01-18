# -*- coding: utf-8 -*-

"""
Module to provide a simulator to render a laparoscopic view comprising
models of anatomy along with a laparoscopic ultrasound probe.
"""

import numpy as np
import vtk
import sksurgerycore.transforms.matrix as cmu
import sksurgeryvtk.widgets.vtk_rendering_generator as rg
import sksurgeryvtk.utils.matrix_utils as vmu


class VTKLUSSimulator(rg.VTKRenderingGenerator):
    """
    Class derived from VTKRenderingGenerator to provide additional
    functions to set up the position of anatomy and LUS probe with
    respect to a stationary camera, placed at the world origin,
    and pointing along +ve z axis, as per OpenCV conventions.

    Note: The mesh representing the LUS probe body must be called 'probe',
    and there must be at least one other mesh called 'liver'. Any other
    meshes, e.g. gallbladder, arterties etc., will have the same transform
    applied as the liver surface.

    :param models_json_file: JSON file describing VTK models, in SNAPPY format
    :param background_image_file: RGB image to render in background
    :param camera_intrinsics_file: [3x3] matrix in text file, in numpy format
    :param liver2camera_reference_file: [4x4] matrix in text file, numpy format
    :param probe2camera_reference_file: [4x4] matrix in text file, numpy format
    """
    def __init__(self,
                 models_json_file,
                 background_image_file,
                 camera_intrinsics_file,
                 liver2camera_reference_file,
                 probe2camera_reference_file,
                 camera_to_world=None,
                 left_to_right=None,
                 clipping_range=(1, 1000)
                 ):
        super().__init__(models_json_file,
                         background_image_file,
                         camera_intrinsics_file,
                         camera_to_world=camera_to_world,
                         left_to_right=left_to_right,
                         zbuffer=False,
                         gaussian_sigma=0,
                         gaussian_window_size=11,
                         clipping_range=clipping_range
                         )

        self.reference_l2c = np.loadtxt(liver2camera_reference_file)
        self.reference_p2c = np.loadtxt(probe2camera_reference_file)

        self.cyl = vtk.vtkCylinderSource()
        self.cyl.SetResolution(88)
        self.cyl.SetRadius(5)
        self.cyl.SetHeight(1000)
        self.cyl.SetCenter((0, self.cyl.GetHeight() / 2.0, 0))
        self.cyl.Update()

        self.cyl_matrix = vtk.vtkMatrix4x4()
        self.cyl_matrix.Identity()
        self.cyl_trans = vtk.vtkTransform()
        self.cyl_trans.SetMatrix(self.cyl_matrix)
        self.cyl_transform_filter = vtk.vtkTransformPolyDataFilter()
        self.cyl_transform_filter.SetInputData(self.cyl.GetOutput())
        self.cyl_transform_filter.SetTransform(self.cyl_trans)

        self.cyl_mapper = vtk.vtkPolyDataMapper()
        self.cyl_mapper.SetInputConnection(
            self.cyl_transform_filter.GetOutputPort())
        self.cyl_mapper.Update()
        self.cyl_actor = vtk.vtkActor()
        self.cyl_actor.SetMapper(self.cyl_mapper)

        probe_model = self.model_loader.get_surface_model('probe')
        probe_colour = probe_model.get_colour()
        self.cyl_actor.GetProperty().SetColor(probe_colour)
        if probe_model.get_no_shading():
            self.cyl_actor.GetProperty().SetAmbient(1)
            self.cyl_actor.GetProperty().SetDiffuse(0)
            self.cyl_actor.GetProperty().SetSpecular(0)

        self.overlay.add_vtk_actor(self.cyl_actor)

        self.set_clipping_range(clipping_range[0], clipping_range[1])
        self.setup_camera_extrinsics(camera_to_world, left_to_right)

    def set_pose(self,
                 anatomy_pose_params,
                 probe_pose_params,
                 angle_of_handle,
                 anatomy_location=None
                 ):
        """
        This is the main method to call to setup the pose of all anatomy and
        for the LUS probe, and the handle.

        You can then call get_image() to get the rendered image,
        or call get_masks() to get a set of rendered masks,
        and the relevant pose parameters for ML purposes.

        The liver2camera and probe2camera are returned as 4x4 matrices.
        This is because there are multiple different parameterisations
        that the user might be working in. e.g. Euler angles, Rodrigues etc.

        :param anatomy_pose_params: [rx, ry, rz, tx, ty, tz] in deg/mm
        :param probe_pose_params: [rx, ry, rz, tx, ty, tz] in deg/mm
        :param angle_of_handle: angle in deg
        :param anatomy_location: [1x3] location of random point on liver surface
        :return: [liver2camera4x4, probe2camera4x4, angle, anatomy_location1x3]
        """
        # The 'anatomy_location' picks a point on the surface and moves
        # the LUS probe to have it's centroid based there. This is in effect
        # updating the so-called 'reference' position of the probe.
        # Subsequent offsets in [rx, ry, rz, tx, ty, tz] are from this new posn.
        p2c = self.reference_p2c

        if anatomy_location is not None:
            picked = np.zeros((4, 1))
            picked[0][0] = anatomy_location[0]
            picked[1][0] = anatomy_location[1]
            picked[2][0] = anatomy_location[2]
            picked[3][0] = 1
            picked_point = self.reference_l2c @ picked

            # This p2c then becomes the 'reference_probe2camera'.
            p2c[0][3] = picked_point[0]
            p2c[1][3] = picked_point[1]
            p2c[2][3] = picked_point[2]

        # First we can compute the angle of the handle.
        # This applies directly to the data, as it comes out
        # of the vtkTransformPolyDataFilter, before the actor transformation.
        probe_offset = np.eye(4)
        probe_offset[0][3] = 0.007877540588378196
        probe_offset[1][3] = 36.24640712738037
        probe_offset[2][3] = -3.8626091003417997
        r_x = \
            cmu.construct_rx_matrix(angle_of_handle, is_in_radians=False)
        rotation_about_x = \
            cmu.construct_rigid_transformation(r_x, np.zeros((3, 1)))
        self.cyl_trans.SetMatrix(
            vmu.create_vtk_matrix_from_numpy(probe_offset @ rotation_about_x))
        self.cyl_transform_filter.Update()

        # Now we compute the transformation for the anatomy.
        # We assume that the anatomy has been normalised (zero-centred).
        rotation_tx = vmu.create_matrix_from_list([anatomy_pose_params[0],
                                                   anatomy_pose_params[1],
                                                   anatomy_pose_params[2],
                                                   0, 0, 0],
                                                  is_in_radians=False)
        translation_tx = vmu.create_matrix_from_list([0, 0, 0,
                                                      anatomy_pose_params[3],
                                                      anatomy_pose_params[4],
                                                      anatomy_pose_params[5]],
                                                     is_in_radians=False)
        anatomy_tx = translation_tx @ self.reference_l2c @ rotation_tx
        full_anatomy_tx_vtk = \
            vmu.create_vtk_matrix_from_numpy(anatomy_tx)

        # Now we compute the position of the probe.
        # We assume that the probe model has been normalised (zero-centred).
        probe_tx = vmu.create_matrix_from_list(probe_pose_params,
                                               is_in_radians=False)
        p2l = np.linalg.inv(self.reference_l2c) @ p2c
        probe_actor_tx = p2l @ probe_tx

        full_probe_actor_tx = anatomy_tx @ probe_actor_tx
        full_probe_actor_tx_vtk = \
            vmu.create_vtk_matrix_from_numpy(full_probe_actor_tx)

        # This is where we apply transforms to each actor.
        self.cyl_actor.PokeMatrix(full_probe_actor_tx_vtk)
        probe_model = self.model_loader.get_surface_model('probe')
        probe_model.actor.PokeMatrix(full_probe_actor_tx_vtk)
        for model in self.model_loader.get_surface_models():
            if model.get_name() != 'probe':
                model.actor.PokeMatrix(full_anatomy_tx_vtk)

        # Force re-render
        self.overlay.Render()
        self.repaint()

        # Return parameters for final solution.
        liver_model = self.model_loader.get_surface_model('liver')
        final_l2c = \
            vmu.create_numpy_matrix_from_vtk(liver_model.actor.GetMatrix())
        probe_model = self.model_loader.get_surface_model('probe')
        final_p2c = \
            vmu.create_numpy_matrix_from_vtk(probe_model.actor.GetMatrix())

        return [final_l2c, final_p2c, angle_of_handle, anatomy_location]
