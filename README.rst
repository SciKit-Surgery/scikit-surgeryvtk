scikit-surgeryvtk
===============================

.. image:: https://github.com/UCL/scikit-surgeryvtk /raw/master/weiss_logo.png
   :height: 128px
   :width: 128px
   :target: https://github.com/UCL/scikit-surgeryvtk 
   :alt: Logo

|

.. image:: https://github.com/UCL/scikit-surgeryvtk/workflows/.github/workflows/ci.yml/badge.svg
   :target: https://github.com/UCL/scikit-surgeryvtk/actions
   :alt: GitHub Actions CI statuss

.. image:: https://coveralls.io/repos/github/UCL/scikit-surgeryvtk/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/UCL/scikit-surgeryvtk?branch=master
    :alt: Test coverage

.. image:: https://readthedocs.org/projects/scikit-surgeryvtk /badge/?version=latest
    :target: http://scikit-surgeryvtk .readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

scikit-surgeryvtk implements VTK for Image Guided Surgery applications.

scikit-surgeryvtk is part of the `SNAPPY`_ software project, developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_, part of `University College London (UCL)`_.

.. features-start

Features
--------
Functionality includes:

* `Load 3D models <https://scikit-surgeryvtk.readthedocs.io/en/latest/models/index.html>`_ from vtl/stl/vtp etc. files.
* `A widget to overlay <https://scikit-surgeryvtk.readthedocs.io/en/latest/widgets/index.html#module-sksurgeryvtk.widgets.vtk_overlay_window>`_ 3D models onto a background image e.g. from webcam/video file, useful for Augmented Reality (AR) overlays, using VTK.
* Functions for working with `calibrated cameras <https://scikit-surgeryvtk.readthedocs.io/en/latest/camera/index.html>`_, and projecting points from 3D to 2D.
* A widget to drive a `stereo interlaced monitor <https://scikit-surgeryvtk.readthedocs.io/en/latest/widgets/index.html#module-sksurgeryvtk.widgets.vtk_interlaced_stereo_window>`_.
* Functions to `voxelise data and calculate distance fields <https://scikit-surgeryvtk.readthedocs.io/en/latest/widgets/index.html#module-sksurgeryvtk.models.voxelise>`_.

.. features-end

Installing
~~~~~~~~~~

You can pip install as follows:
::

    pip install scikit-surgeryvtk


Developing
^^^^^^^^^^

You can clone the repository using the following command:

::

    git clone https://github.com/UCL/scikit-surgeryvtk


Running the tests
^^^^^^^^^^^^^^^^^

You can run the unit tests by installing and running tox:

    ::

      pip install tox
      tox

Encountering Problems?
^^^^^^^^^^^^^^^^^^^^^^
Please get in touch/raise an issue.

Contributing
^^^^^^^^^^^^

Please see the `contributing guidelines`_.


Useful links
^^^^^^^^^^^^

* `Source code repository`_
* `Documentation`_


Licensing and copyright
-----------------------

Copyright 2018 University College London.
scikit-surgeryvtk is released under the BSD-3 license. Please see the `license file`_ for details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/UCL/scikit-surgeryvtk
.. _`Documentation`: https://scikit-surgeryvtk.readthedocs.io
.. _`SNAPPY`: https://weisslab.cs.ucl.ac.uk/WEISS/PlatformManagement/SNAPPY/wikis/home
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/UCL/scikit-surgeryvtk/CONTRIBUTING.rst
.. _`license file`: https://github.com/UCL/scikit-surgeryvtkblob/master/LICENSE
.. _`common issues`: https://weisslab.cs.ucl.ac.uk/WEISS/SoftwareRepositories/SNAPPY/scikit-surgery/wikis/Common-Issues
