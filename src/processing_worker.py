"""Выполнение проверки матрицы в отдельном процессе."""

import json
import sys


def main():
    try:
        from .processing_module import is_symmetric

        matrix = json.load(sys.stdin)
        result = is_symmetric(matrix)
        json.dump(result, sys.stdout)
        return 0
    except ImportError as error:
        print(f"Модуль вычислений недоступен: {error}", file=sys.stderr)
        return 2
    except (ValueError, TypeError, OverflowError) as error:
        print(f"Ошибка данных: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
