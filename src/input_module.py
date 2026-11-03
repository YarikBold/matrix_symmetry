"""Ввод квадратной матрицы."""

from math import isfinite


def input_size():
    while True:
        try:
            n = int(input("Введите размерность матрицы n: "))
            if n > 0:
                return n
            print("Ошибка: размерность должна быть положительной.")
        except ValueError:
            print("Ошибка: введите целое число.")


def input_matrix(n):
    matrix = []
    print("Введите элементы матрицы построчно:")
    for i in range(n):
        while True:
            try:
                row = list(map(float, input(f"Строка {i + 1}: ").split()))
                if len(row) != n:
                    print(f"Ошибка: необходимо ввести ровно {n} чисел.")
                    continue
                if not all(isfinite(value) for value in row):
                    print("Ошибка: введите только конечные числа.")
                    continue
                matrix.append(row)
                break
            except ValueError:
                print("Ошибка: все элементы должны быть числами.")
    return matrix
