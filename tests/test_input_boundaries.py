from unittest.mock import patch

import pytest

from src.input_module import input_matrix, input_size


@pytest.mark.parametrize("size", ["-1", "0"])
def test_size_below_minimum_requests_input_again(size, capsys):
    with patch("builtins.input", side_effect=[size, "1"]):
        result = input_size()

    assert result == 1
    assert "размерность должна быть положительной" in capsys.readouterr().out


@pytest.mark.parametrize("size", [1, 2])
def test_size_accepts_minimum_and_next_value(size, capsys):
    with patch("builtins.input", return_value=str(size)):
        result = input_size()

    assert result == size
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("row", ["1", "1 2 3"])
def test_row_length_one_below_or_above_expected(row, capsys):
    with patch("builtins.input", side_effect=[row, "1 2", "2 3"]):
        matrix = input_matrix(2)

    assert matrix == [[1.0, 2.0], [2.0, 3.0]]
    assert "необходимо ввести ровно 2 чисел" in capsys.readouterr().out
