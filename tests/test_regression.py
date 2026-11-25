import json
from math import nextafter
from pathlib import Path
import subprocess
import sys

import pytest


pytestmark = pytest.mark.regression
ROOT = Path(__file__).resolve().parents[1]


def write_request(path, values, version="1.0"):
    payload = {
        "version": version,
        "request_id": "lab4-regression",
        "dimension": len(values),
        "values": values,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def run_cli(request, response):
    return subprocess.run(
        [
            sys.executable, "-X", "utf8", "src/main.py",
            "--input", str(request), "--output", str(response),
        ],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=10,
    )


@pytest.mark.parametrize(
    "values, expected",
    [
        ([[1.0, 2.0], [2.0, 3.0]], True),
        ([[1.0, 2.0], [nextafter(2.0, 3.0), 3.0]], False),
    ],
    ids=["symmetric", "one-float-step"],
)
def test_direct_script_keeps_symmetry_contract(tmp_path, values, expected):
    request = tmp_path / "request.json"
    response = tmp_path / "response.json"
    write_request(request, values)
    original = request.read_bytes()

    result = run_cli(request, response)

    assert result.returncode == 0, result.stderr
    assert request.read_bytes() == original
    assert json.loads(response.read_text(encoding="utf-8")) == {
        "version": "1.0",
        "request_id": "lab4-regression",
        "size": 2,
        "is_symmetric": expected,
    }


def test_direct_script_refuses_another_name_for_input_file(tmp_path):
    request = tmp_path / "request.json"
    alias = tmp_path / "alias.json"
    write_request(request, [[7]])
    original = request.read_bytes()
    alias.hardlink_to(request)

    result = run_cli(request, alias)

    assert result.returncode == 1
    assert "Файлы запроса и ответа должны различаться" in result.stderr
    assert request.read_bytes() == alias.read_bytes() == original


def test_direct_script_refuses_unknown_protocol_version(tmp_path):
    request = tmp_path / "request.json"
    response = tmp_path / "response.json"
    write_request(request, [[7]], version="2.0")

    result = run_cli(request, response)

    assert result.returncode == 1
    assert "Неподдерживаемая версия формата" in result.stderr
    assert not response.exists()
