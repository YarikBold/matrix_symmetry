import json

from src.main import run_json


def test_input_file_is_preserved_when_paths_match(tmp_path, capsys):
    request = tmp_path / "request.json"
    original = json.dumps({
        "version": "1.0",
        "request_id": "same-path",
        "dimension": 1,
        "values": [[7]],
    })
    request.write_text(original, encoding="utf-8")

    code = run_json(request, request)

    assert request.read_text(encoding="utf-8") == original
    assert code == 1
    assert "Файлы запроса и ответа должны различаться" in capsys.readouterr().err
