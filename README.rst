scikit-surgeryvtk
===============================

.. image:: https://raw.githubusercontent.com/SciKit-Surgery/scikit-surgeryvtk/master/sksvtk_logo.png
   :height: 128px
   :width: 128px
   :target: https://github.com/SciKit-Surgery/scikit-surgeryvtk 
   :alt: Logo

|

.. image:: https://github.com/SciKit-Surgery/scikit-surgeryvtk/workflows/.github/workflows/ci.yml/badge.svg
   :target: https://github.com/SciKit-Surgery/scikit-surgeryvtk/actions
   :alt: GitHub Actions CI status

.. image:: https://coveralls.io/repos/github/SciKit-Surgery/scikit-surgeryvtk/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/SciKit-Surgery/scikit-surgeryvtk?branch=master
    :alt: Test coverage

.. image:: https://readthedocs.org/projects/scikit-surgeryvtk /badge/?version=latest
    :target: http://scikit-surgeryvtk .readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/Cite-SciKit--Surgery-informational
   :target: https://doi.org/10.1007/s11548-020-02180-5
   :alt: The SciKit-Surgery paper

.. image:: https://img.shields.io/twitter/follow/scikit_surgery?style=social
   :target: https://twitter.com/scikit_surgery?ref_src=twsrc%5Etfw
   :alt: Follow scikit_surgery on twitter

Author(s): Stephen Thompson, Matt Clarkson, Thomas Dowrick and Miguel Xochicale;
Contributor(s): Mian Ahmad.

scikit-surgeryvtk implements VTK for Image Guided Surgery applications.

scikit-surgeryvtk is part of the `SciKit-Surgery`_ software project, developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_, part of `University College London (UCL)`_.

scikit-surgeryvtk is tested on Python 3.8. and may support other Python versions.

.. features-start

Features
--------
Functionality includes:

* `Load 3D surface models <https://scikit-surgeryvtk.readthedocs.io/en/latest/module_ref.html#module-sksurgeryvtk.models.vtk_surface_model>`_ from vtl/stl/vtp etc. files.
* `A widget to overlay <https://scikit-surgeryvtk.readthedocs.io/en/latest/module_ref.html#overlay-widget>`_ 3D models onto a background image e.g. from webcam/video file, useful for Augmented Reality (AR) overlays, using VTK.
* Functions for working with `calibrated cameras <https://scikit-surgeryvtk.readthedocs.io/en/latest/module_ref.html#module-sksurgeryvtk.camera.vtk_camera_model>`_, and projecting points from 3D to 2D.
* A widget to drive a `stereo interlaced monitor <https://scikit-surgeryvtk.readthedocs.io/en/latest/module_ref.html#module-sksurgeryvtk.widgets.vtk_interlaced_stereo_window>`_.
* Functions to `voxelise data and calculate distance fields <https://scikit-surgeryvtk.readthedocs.io/en/latest/module_ref.html#module-sksurgeryvtk.models.voxelise>`_.

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

    git clone https://github.com/SciKit-Surgery/scikit-surgeryvtk


Running the tests
^^^^^^^^^^^^^^^^^

You can run the unit tests, build documentation, and other options by installing and running tox:

::

    pip install tox
    tox
    tox -e docs
    tox -e lint


Encountering Problems?
^^^^^^^^^^^^^^^^^^^^^^
Please get in touch or raise an `issue`_.


Contributing
^^^^^^^^^^^^

Please see the `contributing guidelines`_.


Useful links
^^^^^^^^^^^^

* `Source code repository`_
* `Documentation`_


Licensing and copyright
-----------------------

Copyright 2020 University College London.
scikit-surgeryvtk is released under the BSD-3 license. Please see the `license file`_ for details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/SciKit-Surgery/scikit-surgeryvtk
.. _`Documentation`: https://scikit-surgeryvtk.readthedocs.io
.. _`SciKit-Surgery`: https://github.com/SciKit-Surgery/scikit-surgery/wiki/home
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/SciKit-Surgery/scikit-surgeryvtk/blob/master/CONTRIBUTING.rst
.. _`license file`: https://github.com/SciKit-Surgery/scikit-surgeryvtkblob/master/LICENSE
.. _`common issues`: https://weisslab.cs.ucl.ac.uk/WEISS/SoftwareRepositories/SNAPPY/scikit-surgery/wikis/Common-Issues
.. _`issue`: https://github.com/SciKit-Surgery/scikit-surgeryvtk/issues/new