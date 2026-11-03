"""Управление модулями и обработка ошибок интеграции."""

import argparse
import sys

if __package__:
    from .input_module import input_size, input_matrix
    from .processing_module import is_symmetric
    from .output_module import print_result
    from .json_transport import (
        load_request, map_request, make_response, save_response,
    )
    from .integration_service import check_matrix, ModuleUnavailableError
else:
    from input_module import input_size, input_matrix
    from processing_module import is_symmetric
    from output_module import print_result
    from json_transport import (
        load_request, map_request, make_response, save_response,
    )
    from integration_service import check_matrix, ModuleUnavailableError


def main(checker=is_symmetric):
    try:
        n = input_size()
        matrix = input_matrix(n)
        result = checker(matrix)
        print_result(result)
        return 0
    except ValueError as error:
        print(f"Ошибка взаимодействия модулей: {error}")
    except EOFError:
        print("\nВвод завершён до получения всех данных.")
    except KeyboardInterrupt:
        print("\nРабота прервана пользователем.")
    return 1


def run_json(input_path, output_path, checker=None, timeout=5.0):
    try:
        payload = load_request(input_path)
        data = map_request(payload)
        if checker is None:
            result = check_matrix(data["matrix"], timeout=timeout)
        else:
            result = checker(data["matrix"])
        response = make_response(data, result)
        save_response(output_path, response)
        print_result(result)
        print(f"Ответ сохранён: {output_path}")
        return 0
    except TimeoutError as error:
        print(f"Таймаут интеграции: {error}", file=sys.stderr)
    except ModuleUnavailableError as error:
        print(f"Недоступность модуля: {error}", file=sys.stderr)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Ошибка JSON-обмена: {error}", file=sys.stderr)
    return 1


def cli():
    parser = argparse.ArgumentParser(
        description="Проверка симметричности матрицы."
    )
    parser.add_argument("--input", help="Путь к JSON-запросу.")
    parser.add_argument("--output", help="Путь к JSON-ответу.")
    parser.add_argument(
        "--timeout", type=float, default=5.0,
        help="Время ожидания вычислений в файловом режиме, секунды.",
    )
    args = parser.parse_args()

    if (args.input is None) != (args.output is None):
        parser.error("--input и --output нужно указывать вместе.")
    if args.input is not None:
        return run_json(args.input, args.output, timeout=args.timeout)
    return main()


if __name__ == "__main__":
    sys.exit(cli())
