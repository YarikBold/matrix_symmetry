"""Проверка симметричности квадратной матрицы."""

from math import isfinite


def is_symmetric(matrix):
    """Возвращает результат проверки или сообщает об ошибке данных."""
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("Матрица должна быть непустым списком.")

    n = len(matrix)
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("Матрица должна быть квадратной.")
        for value in row:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise ValueError("Элементы должны быть конечными числами.")

    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] != matrix[j][i]:
                return False
    return True
