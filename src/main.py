def input_size():
    while True:
        try:
            n = int(input("Введите размерность матрицы n: "))
            if n > 0:
                return n
            print("Ошибка: размерность должна быть положительным числом.")
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

                matrix.append(row)
                break
            except ValueError:
                print("Ошибка: все элементы должны быть числами.")

    return matrix


def is_symmetric(matrix):
    n = len(matrix)

    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] != matrix[j][i]:
                return False

    return True


def print_result(result):
    if result:
        print("Матрица является симметричной относительно главной диагонали.")
    else:
        print("Матрица не является симметричной относительно главной диагонали.")


def main():
    n = input_size()
    matrix = input_matrix(n)
    result = is_symmetric(matrix)
    print_result(result)


if __name__ == "__main__":
    main()
