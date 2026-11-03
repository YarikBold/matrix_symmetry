"""Обмен JSON-сообщениями и сопоставление данных."""

import json
from math import isfinite


PROTOCOL_VERSION = "1.0"


def load_request(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def map_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("Запрос должен быть JSON-объектом.")
    if payload.get("version") != PROTOCOL_VERSION:
        raise ValueError("Неподдерживаемая версия формата.")

    request_id = payload.get("request_id")
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("Не указан идентификатор запроса.")

    dimension = payload.get("dimension")
    if isinstance(dimension, bool) or not isinstance(dimension, (str, int)):
        raise ValueError("Размер должен быть целым числом или строкой.")
    try:
        n = int(dimension)
    except ValueError as error:
        raise ValueError("Некорректный размер матрицы.") from error
    if n <= 0:
        raise ValueError("Размер должен быть положительным.")

    values = payload.get("values")
    if not isinstance(values, list) or len(values) != n:
        raise ValueError("Количество строк не совпадает с размером.")

    matrix = []
    for row in values:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("Количество элементов строки неверно.")
        converted = []
        for value in row:
            if isinstance(value, bool) or not isinstance(
                value, (str, int, float)
            ):
                raise ValueError("Недопустимый тип элемента.")
            try:
                number = float(value)
            except (ValueError, OverflowError) as error:
                raise ValueError("Элемент нельзя преобразовать в число.") from error
            if not isfinite(number):
                raise ValueError("Элементы должны быть конечными числами.")
            converted.append(number)
        matrix.append(converted)

    return {"request_id": request_id, "n": n, "matrix": matrix}


def make_response(data, result):
    if not isinstance(result, bool):
        raise ValueError("Результат проверки должен иметь тип bool.")
    return {
        "version": PROTOCOL_VERSION,
        "request_id": data["request_id"],
        "size": data["n"],
        "is_symmetric": result,
    }


def save_response(path, response):
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(
            response, stream, ensure_ascii=False, indent=2, allow_nan=False
        )
        stream.write("\n")
