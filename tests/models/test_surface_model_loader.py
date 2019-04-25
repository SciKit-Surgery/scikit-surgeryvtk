# -*- coding: utf-8 -*-

import pytest
from sksurgeryvtk.models.surface_model_loader import SurfaceModelLoader
from sksurgerycore.configuration.configuration_manager import ConfigurationManager
import sksurgerycore.utilities.validate_file as vf


def check_surface_properties(surface):
    assert isinstance(surface, dict)
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

    pickable_value = surface['pickable']
    assert isinstance(pickable_value, bool)

def test_empty_surface_config():
    config = ConfigurationManager('tests/data/config/invalid_config.json')
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
    assert len(surfaces.keys()) == 2
    assert len(surfaces.values()) == 2

    for name in surfaces:
        assert isinstance(name, str)
        surface = surfaces[name]
        check_surface_properties(surface)

    assemblies = data['assemblies']
    assert len(assemblies.keys()) == 1

    assembly = next(iter(assemblies))
    for surface in assemblies[assembly]:
        assert surface in surfaces.keys()


def test_surface_model_loader_2_surface_no_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_two.json')
    config_data = config.get_copy()
    loader = SurfaceModelLoader(config_data)
    assert loader is not None
    assert len(loader.get_assembly_names()) == 0
    assert len(loader.get_surface_model_names()) == 2


def test_surface_model_loader_2_surface_with_assembly():
    config = ConfigurationManager('tests/data/config/surface_model_two_in_assembly.json')
    config_data = config.get_copy()
    loader = SurfaceModelLoader(config_data)
    assert loader is not None
    assert len(loader.get_assembly_names()) == 1
    assert len(loader.get_surface_model_names()) == 2

    # Call these functions for coverage purposes
    loader.get_assembly("veins")
    loader.get_surface_model("portal veins")


def test_surface_model_loader_2_in_assembly_on_its_own(vtk_overlay):
    config = ConfigurationManager('tests/data/config/surface_model_two_assemblies.json')
    config_data = config.get_copy()
    loader = SurfaceModelLoader(config_data)
    assert loader is not None
    assert len(loader.get_assembly_names()) == 2
    assert len(loader.get_surface_model_names()) == 3
    widget, _, _, app = vtk_overlay
    widget.add_vtk_models(loader.get_surface_models())
    widget.show()
    #app.exec_()


def test_no_surfaces_raises_error():
    config = ConfigurationManager('tests/data/config/invalid_config.json')
    config_data = config.get_copy()
    with pytest.raises(KeyError):
        SurfaceModelLoader(config_data)


def test_assembly_surface_doesnt_exist_raises_error():
    config = ConfigurationManager('tests/data/config/invalid_surface_in_assembly.json')
    config_data = config.get_copy()
    with pytest.raises(KeyError):
        SurfaceModelLoader(config_data)


def test_duplicate_surface_in_assembly_raises_error():
    config = ConfigurationManager('tests/data/config/surface_model_duplicates_in_assembly.json')
    config_data = config.get_copy()
    with pytest.raises(ValueError):
        SurfaceModelLoader(config_data)
