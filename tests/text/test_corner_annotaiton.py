# coding=utf-8

import pytest

from sksurgeryvtk.text.text_overlay import VTKCornerAnnotation


@pytest.fixture
def corner_annotaiton():
    corner_annotaiton = VTKCornerAnnotation()
    return corner_annotaiton


def test_non_list_input_raises_error(corner_annotaiton):
    invalid_input = 1
    with pytest.raises(TypeError):
        corner_annotaiton.set_text(invalid_input)


def test_invalid_size_input_raises_error(corner_annotaiton):
    invalid_input = ["1", "2", "3"]
    with pytest.raises(ValueError):
        corner_annotaiton.set_text(invalid_input)


def test_non_string_in_list_raises_error(corner_annotaiton):
    invalid_input = ["1", "2", 3, "4"]
    with pytest.raises(ValueError):
        corner_annotaiton.set_text(invalid_input)


def test_none_in_list_raises_error(corner_annotaiton):
    invalid_input = ["1", "2", None, "4"]
    with pytest.raises(ValueError):
        corner_annotaiton.set_text(invalid_input)


def test_valid_input_raises_no_error(corner_annotaiton):
    valid_input = ["1", "2", "3", "4"]
    corner_annotaiton.set_text(valid_input)


def test_setter_getter(corner_annotaiton):
    initial = corner_annotaiton.get_text()
    assert len(initial) == 4
    assert initial[0] is ''
    assert initial[1] is ''
    assert initial[2] is ''
    assert initial[3] is ''
    stuff_to_set = ['Snappy', 'is', 'totally', 'awesome']
    corner_annotaiton.set_text(stuff_to_set)
    stuff_retrieved = corner_annotaiton.get_text()
    assert stuff_to_set == stuff_retrieved
