# -*- coding: utf-8 -*-

import pytest
from sksurgeryvtk.models.surface_model_loader import SurfaceModelLoader
from sksurgerycore.configuration.configuration_manager import ConfigurationManager
import sksurgerycore.utilities.validate_file as vf


def check_surface_properties(surface):
    assert isinstance(surface, dict)
    object_type = surface['type']
    assert object_type is not None
    assert object_type == 'surface'
    file_name = surface['file']
    assert file_name is not None
    vf.validate_is_file(file_name)
    colour_value = surface['colour']
    assert isinstance(colour_value, list)
    assert len(colour_value) == 3
    assert isinstance(colour_value[0], int)
    assert colour_value[0] >= 0
    assert colour_value[0] <= 255
    assert isinstance(colour_value[1], int)
    assert colour_value[1] >= 0
    assert colour_value[1] <= 255
    assert isinstance(colour_value[2], int)
    assert colour_value[2] >= 0
    assert colour_value[2] <= 255
    opacity_value = surface['opacity']
    assert isinstance(opacity_value, float)
    assert opacity_value >= 0.0
    assert opacity_value <= 1.0
    visibility_value = surface['visibility']
    assert isinstance(visibility_value, bool)


def test_empty_surface_config():
    config = ConfigurationManager('tests/data/config/empty_config.json')
    data = config.get_copy()
    assert isinstance(data, dict)
    assert 'surfaces' not in data.keys()


def test_one_surface_no_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_one.json')
    data = config.get_copy()
    assert isinstance(data, dict)
    surfaces = data['surfaces']
    assert isinstance(surfaces, dict)
    assert len(surfaces.keys()) == 1
    assert len(surfaces.values()) == 1
    name = next(iter(surfaces))
    assert name == 'liver'
    check_surface_properties(surfaces[name])


def test_two_surfaces_no_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_two.json')
    data = config.get_copy()
    surfaces = data['surfaces']
    assert len(surfaces.keys()) == 2
    assert len(surfaces.values()) == 2
    for name in surfaces:
        assert isinstance(name, str)
        surface = surfaces[name]
        check_surface_properties(surface)


def test_two_surface_in_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_two_in_assembly.json')
    data = config.get_copy()
    surfaces = data['surfaces']
    assert len(surfaces.keys()) == 1
    assert len(surfaces.values()) == 1
    for outer_name in surfaces:
        assert isinstance(outer_name, str)
        thing = surfaces[outer_name]
        assert isinstance(thing, dict)
        for inner_name in thing:
            if inner_name == 'type':
                assert isinstance(inner_name, str)
            else:
                surface = thing[inner_name]
                check_surface_properties(surface)


def test_surface_model_loader_2_surface_no_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_two.json')
    loader = SurfaceModelLoader(config)
    assert loader is not None
    assert len(loader.get_assembly_names()) == 0
    assert len(loader.get_surface_model_names()) == 2


def test_surface_model_loader_2_surface_with_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_two_in_assembly.json')
    loader = SurfaceModelLoader(config)
    assert loader is not None
    assert len(loader.get_assembly_names()) == 1
    assert len(loader.get_surface_model_names()) == 2


def test_surface_model_loader_2_in_assembly_on_on_its_own():
    config = ConfigurationManager('tests/data/config/surface_model_two_in_assembly_one_on_its_own.json')
    loader = SurfaceModelLoader(config)
    assert loader is not None
    assert len(loader.get_assembly_names()) == 1
    assert len(loader.get_surface_model_names()) == 3
