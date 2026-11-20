"""Точка входа приложения."""

import sys

from depgraph.cli import parse_args
from depgraph.errors import AppError, ConfigError
from depgraph.nuget import get_dependencies

EXIT_OK = 0
EXIT_ERROR = 2
ANY_VERSION = "*"


def run(config):
    """Выводит прямые зависимости заданного пакета."""
    if config.test_mode:
        raise ConfigError("тестовый режим появится на этапе 3")
    found = get_dependencies(config.repo, config.package, config.version)
    print(f"Прямые зависимости {config.package} {config.version}:")
    if not found:
        print("  (нет)")
    for dependency in found:
        print(f"  {dependency.name} {dependency.version_range or ANY_VERSION}")


def main(argv=None):
    """Запускает приложение и возвращает код завершения."""
    try:
        run(parse_args(argv))
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
