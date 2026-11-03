"""Интеграционные тесты программы через командную строку."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestIntegration(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.request = self.folder / "request.json"
        self.response = self.folder / "response.json"
        self.payload = {
            "version": "1.0",
            "request_id": "test-001",
            "dimension": "2",
            "values": [["1", "2"], ["2", "3"]],
        }

    def run_cli(self, *args, input_text=None):
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, "-m", "src.main", *args],
            cwd=ROOT,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
            timeout=10,
        )

    def write_request(self):
        self.request.write_text(
            json.dumps(self.payload), encoding="utf-8"
        )

    def run_files(self):
        return self.run_cli(
            "--input", str(self.request),
            "--output", str(self.response),
        )

    def test_file_exchange(self):
        cases = [
            ([["1", "2"], ["2", "3"]], True),
            ([["1", "2"], ["3", "4"]], False),
        ]
        for values, expected in cases:
            with self.subTest(expected=expected):
                self.payload["values"] = values
                self.write_request()
                result = self.run_files()
                self.assertEqual(result.returncode, 0, result.stderr)
                response = json.loads(
                    self.response.read_text(encoding="utf-8")
                )
                self.assertEqual(response, {
                    "version": "1.0",
                    "request_id": "test-001",
                    "size": 2,
                    "is_symmetric": expected,
                })
                self.assertIsInstance(response["size"], int)
                self.assertIsInstance(response["is_symmetric"], bool)

    def test_invalid_json(self):
        self.request.write_text("{broken", encoding="utf-8")
        result = self.run_files()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr)
        self.assertFalse(self.response.exists())

    def test_invalid_matrix(self):
        cases = [
            [["1"]],
            [["abc", "2"], ["2", "3"]],
            [["inf", "2"], ["2", "3"]],
        ]
        for values in cases:
            with self.subTest(values=values):
                self.payload["values"] = values
                self.write_request()
                result = self.run_files()
                self.assertEqual(result.returncode, 1)
                self.assertTrue(result.stderr)
                self.assertFalse(self.response.exists())

    def test_missing_input(self):
        result = self.run_files()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr)
        self.assertFalse(self.response.exists())

    def test_incomplete_arguments(self):
        result = self.run_cli("--input", str(self.request))
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr)
        self.assertFalse(self.response.exists())

    def test_interactive_mode(self):
        result = self.run_cli(input_text="2\n1 2\n3 4\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Матрица не является симметричной", result.stdout)


if __name__ == "__main__":
    unittest.main()
