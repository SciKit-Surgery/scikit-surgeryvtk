# coding=utf-8
"""
Setup for scikit-surgeryvtk
"""

from setuptools import setup, find_packages
import versioneer

# Get the long description
with open('README.rst') as f:
    long_description = f.read()

setup(
    name='scikit-surgeryvtk',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='scikit-surgeryvtk implements VTK for Image Guided Surgery applications',
    long_description=long_description,
    url='https://github.com/SciKit-Surgery/scikit-surgeryvtk',
    author='Thomas Dowrick',
    author_email='t.dowrick@ucl.ac.uk',
    license='BSD-3 license',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',


        'License :: OSI Approved :: BSD License',


        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    keywords='medical imaging',

    packages=find_packages(
        exclude=[
            'doc',
            'tests',
        ]
    ),

    install_requires=[
        'numpy>=1.11',
        'vtk<=9.1.0',
        'PySide2<5.15.0',
        'opencv-contrib-python-headless>=4.2.0.32',
        'scikit-surgerycore>=0.1.7',
        'scikit-surgeryimage>=0.10.1',
    ],

    entry_points={
        'console_scripts': [
        ],
    },
)
