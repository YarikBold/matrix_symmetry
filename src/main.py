"""Управление взаимодействием модулей."""

if __package__:
    from .input_module import input_size, input_matrix
    from .processing_module import is_symmetric
    from .output_module import print_result
else:
    from input_module import input_size, input_matrix
    from processing_module import is_symmetric
    from output_module import print_result


def main(checker=is_symmetric):
    try:
        n = input_size()
        matrix = input_matrix(n)
        result = checker(matrix)
        print_result(result)
    except ValueError as error:
        print(f"Ошибка взаимодействия модулей: {error}")
    except EOFError:
        print("\nВвод завершён до получения всех данных.")
    except KeyboardInterrupt:
        print("\nРабота прервана пользователем.")


if __name__ == "__main__":
    main()
