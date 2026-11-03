"""Проверки исключительных ситуаций при интеграции."""

from contextlib import redirect_stdout, redirect_stderr
from functools import partial
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.integration_service import check_matrix
from src.main import main, run_json


class TestIntegrationFailures(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.request = self.folder / "request.json"
        self.response = self.folder / "response.json"
        self.payload = {
            "version": "1.0",
            "request_id": "failure-test",
            "dimension": "2",
            "values": [["1", "2"], ["2", "3"]],
        }
        self.write_payload(self.payload)

    def write_payload(self, payload):
        self.request.write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def invoke(self, checker=None, timeout=5.0):
        errors = StringIO()
        with redirect_stdout(StringIO()), redirect_stderr(errors):
            code = run_json(
                self.request, self.response,
                checker=checker, timeout=timeout,
            )
        return code, errors.getvalue()

    def test_timeout(self):
        error = subprocess.TimeoutExpired("worker", 0.1)
        with patch(
            "src.integration_service.subprocess.run",
            side_effect=error,
        ):
            code, message = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("Таймаут интеграции", message)
        self.assertFalse(self.response.exists())

    def test_unavailable_module(self):
        checker = partial(
            check_matrix,
            worker_module="src.nonexistent_processing_worker_for_test",
        )
        code, message = self.invoke(checker=checker)
        self.assertEqual(code, 1)
        self.assertIn("Недоступность модуля", message)
        self.assertFalse(self.response.exists())

    def test_process_launch_error(self):
        with patch(
            "src.integration_service.subprocess.run",
            side_effect=OSError("Запуск недоступен"),
        ):
            code, message = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("Недоступность модуля", message)
        self.assertFalse(self.response.exists())

    def test_invalid_worker_response(self):
        for output in ["broken JSON", "123"]:
            with self.subTest(output=output):
                completed = subprocess.CompletedProcess(
                    args=[], returncode=0, stdout=output, stderr=""
                )
                with patch(
                    "src.integration_service.subprocess.run",
                    return_value=completed,
                ):
                    code, message = self.invoke()
                self.assertEqual(code, 1)
                self.assertTrue(message)
                self.assertFalse(self.response.exists())

    def test_version_conflict(self):
        self.payload["version"] = "2.0"
        self.write_payload(self.payload)
        code, message = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("Неподдерживаемая версия", message)
        self.assertFalse(self.response.exists())

    def test_invalid_request_fields(self):
        cases = [
            None,
            dict(self.payload, request_id=""),
            dict(self.payload, dimension=True),
            dict(self.payload, dimension="abc"),
            dict(self.payload, dimension="0"),
            dict(self.payload, values=[["1", "2"], "bad"]),
            dict(self.payload, values=[[True, "2"], ["2", "3"]]),
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                self.write_payload(payload)
                code, message = self.invoke()
                self.assertEqual(code, 1)
                self.assertTrue(message)
                self.assertFalse(self.response.exists())

    def test_invalid_timeout(self):
        for timeout in [0, -1, float("nan"), float("inf")]:
            with self.subTest(timeout=timeout):
                code, message = self.invoke(timeout=timeout)
                self.assertEqual(code, 1)
                self.assertIn("Таймаут должен быть", message)
                self.assertFalse(self.response.exists())

    def test_invalid_checker_result(self):
        code, message = self.invoke(checker=lambda matrix: "yes")
        self.assertEqual(code, 1)
        self.assertIn("тип bool", message)
        self.assertFalse(self.response.exists())

    def test_output_unavailable(self):
        self.response = self.folder
        code, message = self.invoke(checker=lambda matrix: True)
        self.assertEqual(code, 1)
        self.assertIn("Ошибка JSON-обмена", message)


class TestInteractiveFailures(unittest.TestCase):
    def test_input_recovery(self):
        inputs = [
            "0", "abc", "2", "1", "a b",
            "inf 2", "1 2", "2 3",
        ]
        output = StringIO()
        with patch("builtins.input", side_effect=inputs):
            with redirect_stdout(output):
                code = main()
        self.assertEqual(code, 0)
        self.assertIn("Матрица является симметричной", output.getvalue())
        self.assertIn("Ошибка", output.getvalue())

    def test_interrupted_input(self):
        errors = [EOFError(), KeyboardInterrupt(), ValueError("test")]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                with patch("src.main.input_size", side_effect=error):
                    with redirect_stdout(StringIO()):
                        code = main()
                self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
