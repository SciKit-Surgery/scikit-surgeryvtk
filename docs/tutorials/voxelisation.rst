Distance Field Calcualtion & Voxelisation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This tutorial demonstrates how to generate voxelised data and calculate distance fields, originally
for use with the `Volume2SurfaceCNN <https://gitlab.com/nct_tso_public/Volume2SurfaceCNN>`_ model.

We will use the example of a liver model and intraoperative surface, but this can be applied to any 3D
model and partial surface. Data used for this example can be found in the `GitHub repository <https://github.com/SciKit-Surgery/scikit-surgeryvtk>`_.

.. image:: ./voxelisation_images/voxelisation.png
  :width: 50%

**Figure 1 - Original model/surface (left) and voxelised model/surface (right)**

Creating a signed distance field from a 3D model
------------------------------------------------

Setup parameters:

.. code-block:: python

    import numpy as np
    from sksurgeryvtk.models import voxelise

.. literalinclude:: ../../tests/models/test_voxelise.py
    :language: python
    :start-after: #Tutorial-section-1-start
    :end-before: #Tutorial-section-1-end

The input mesh is expected to be in metres. If it is in mm, as above, we pass a scale factor of 0.001.
Run voxelisation function:

.. literalinclude:: ../../tests/models/test_voxelise.py
    :language: python
    :start-after: #Tutorial-section-2-start
    :end-before: #Tutorial-section-2-end

The `voxelise` function returns a vtkStructuredGrid, but it also writes the data
to the file specified by `output_grid`, which now contains a 3D volume, and a
data array `preoperativeSurface`, which stores the distance value for each
voxel in the grid.

Negative distance values indicate that the element is inside the surface. We can
use this property to visualise the voxelised model using suitable software, e.g. ParaView.

If we apply a threshold filter only showing negative values, this will show the model surface:

.. image:: ./voxelisation_images/preop_threshold.png

Creating an usigned distance field from a surface
-------------------------------------------------

The process for creating a distance field for a surface is similar, except we calculate
the unsigned distance field, which will be stored in a data array 'intraoperativeSurface'.

.. literalinclude:: ../../tests/models/test_voxelise.py
    :language: python
    :start-after: #Tutorial-section-3-start
    :end-before: #Tutorial-section-3-end

The distance field can be calculated from a file, as above, or from a numpy array:

.. literalinclude:: ../../tests/models/test_voxelise.py
    :language: python
    :start-after: #Tutorial-section-4-start
    :end-before: #Tutorial-section-4-end

We can visualise the intraoperative surface, by using a threshold filter between
0 and the (roughly) voxel size, which is equal to `size/grid_elements`

.. image:: ./voxelisation_images/postop_threshold.png

Applying a displacement field to a mesh
---------------------------------------
Once a displacement field has been calcualted (e.g. by V2SNet in `scikit-surgerytorch <https://github.com/UCL/scikit-surgerytorch>`_),
it can be used to displace an input mesh. This could be the orginal preoperative surface, or objects inside the surface model (e.g. vessels, tumors).
Objects outside the surface of the preoperative mesh do not have a valid displacement defined.

The output mesh can optionally be saved by specifying a file name for the save_mesh argument.

.. literalinclude:: ../../tests/models/test_voxelise.py
    :language: python
    :start-after: #Tutorial-section-5-start
    :end-before: #Tutorial-section-5-end

Streamlined Workflow
--------------------

The above examples have been reading/writing vtk data to an output mesh on disk. However,
this can be inefficient if we are repeatedly calling the function, and we can get the same results by just working with the vtk grid in memory instead.
The voxelise function can take a vtkStructuredGrid, instead of a file path, as the `output_grid` agrument.

.. literalinclude:: ../../tests/models/test_voxelise.py
    :language: python
    :start-after: #Tutorial-section-6-start
    :end-before: #Tutorial-section-6-end
