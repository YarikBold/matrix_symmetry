from io import StringIO
import json
import subprocess
import sys
from unittest.mock import patch

import pytest

from src.integration_service import check_matrix
from src.processing_worker import main as worker_main


def test_service_passes_matrix_and_timeout_to_worker():
    finished = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="false", stderr=""
    )
    matrix = [[0, 2], [1, 0]]

    with patch("src.integration_service.subprocess.run", return_value=finished) as run:
        result = check_matrix(matrix, timeout=2.0)

    assert result is False
    assert run.call_args.args[0] == [sys.executable, "-m", "src.processing_worker"]
    assert json.loads(run.call_args.kwargs["input"]) == matrix
    assert run.call_args.kwargs["timeout"] == 2.0


@pytest.mark.parametrize(
    "matrix, expected",
    [("[[1]]", "true"), ("[[0, 2], [1, 0]]", "false")],
    ids=["symmetric", "not-symmetric"],
)
def test_worker_returns_json_boolean(matrix, expected, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO(matrix))

    assert worker_main() == 0
    assert capsys.readouterr().out == expected


def test_worker_reports_invalid_matrix(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("[[1, 2]]"))

    assert worker_main() == 1
    assert "Матрица должна быть квадратной" in capsys.readouterr().err


def test_worker_reports_missing_processing_module(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "src.processing_module", None)

    assert worker_main() == 2
    assert "Модуль вычислений недоступен" in capsys.readouterr().err
