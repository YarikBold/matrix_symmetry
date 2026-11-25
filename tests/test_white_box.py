import pytest

from src.json_transport import map_request
from src.output_module import print_result


@pytest.mark.parametrize(
    "result, expected",
    [
        (True, "Матрица является симметричной относительно главной диагонали."),
        (False, "Матрица не является симметричной относительно главной диагонали."),
    ],
    ids=["symmetric", "not-symmetric"],
)
def test_output_for_both_decisions(result, expected, capsys):
    print_result(result)

    assert capsys.readouterr().out.strip() == expected


def request_with_values(values):
    return {
        "version": "1.0",
        "request_id": "white-box",
        "dimension": 1,
        "values": values,
    }


@pytest.mark.parametrize(
    "values",
    ["", "x", []],
    ids=["wrong-type-wrong-length", "wrong-type-right-length", "list-wrong-length"],
)
def test_rejects_invalid_values_combinations(values):
    with pytest.raises(ValueError, match="Количество строк не совпадает"):
        map_request(request_with_values(values))


def test_accepts_list_with_right_length():
    data = map_request(request_with_values([["7"]]))

    assert data == {"request_id": "white-box", "n": 1, "matrix": [[7.0]]}
    assert isinstance(data["matrix"][0][0], float)
