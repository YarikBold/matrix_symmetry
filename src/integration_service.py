"""Вызов вычислительного модуля с ограничением времени."""

import json
from math import isfinite
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


class ModuleUnavailableError(RuntimeError):
    """Вычислительный процесс недоступен или завершился с ошибкой."""


def check_matrix(matrix, timeout=5.0, worker_module="src.processing_worker"):
    if not isfinite(timeout) or timeout <= 0:
        raise ValueError("Таймаут должен быть положительным конечным числом.")

    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"

    try:
        completed = subprocess.run(
            [sys.executable, "-m", worker_module],
            cwd=ROOT,
            input=json.dumps(matrix, allow_nan=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise TimeoutError(
            "Превышено время ожидания вычислительного модуля."
        ) from error
    except OSError as error:
        raise ModuleUnavailableError(
            "Не удалось запустить вычислительный модуль."
        ) from error

    if completed.returncode != 0:
        message = completed.stderr.strip()
        raise ModuleUnavailableError(
            f"Вычислительный модуль завершился с ошибкой: {message}"
        )

    try:
        result = json.loads(completed.stdout)
    except ValueError as error:
        raise ValueError(
            "Вычислительный модуль вернул некорректный JSON."
        ) from error

    if not isinstance(result, bool):
        raise ValueError("Ответ вычислительного модуля должен иметь тип bool.")
    return result
