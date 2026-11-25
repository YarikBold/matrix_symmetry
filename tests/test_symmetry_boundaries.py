from math import nextafter

import pytest

from src.processing_module import is_symmetric


def test_empty_matrix_is_rejected():
    with pytest.raises(ValueError, match="непустым списком"):
        is_symmetric([])


def test_single_element_matrix_is_symmetric():
    assert is_symmetric([[0.0]]) is True


@pytest.mark.parametrize(
    "value, expected",
    [
        (nextafter(1.0, 0.0), False),
        (1.0, True),
        (nextafter(1.0, 2.0), False),
    ],
    ids=["below", "equal", "above"],
)
def test_symmetry_at_equality_boundary(value, expected):
    matrix = [[0.0, 1.0], [value, 0.0]]

    assert is_symmetric(matrix) is expected
