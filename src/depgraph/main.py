"""Точка входа приложения."""

import sys

from depgraph.cli import parse_args
from depgraph.errors import AppError

EXIT_OK = 0
EXIT_ERROR = 2


def run(config):
    """Выводит все настраиваемые параметры в формате ключ-значение."""
    for key, value in config.as_pairs():
        print(f"{key}: {value}")


def main(argv=None):
    """Запускает приложение и возвращает код завершения."""
    try:
        run(parse_args(argv))
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
