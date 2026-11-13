"""Точка входа: инструмент визуализации графа зависимостей Cargo."""

import sys

from config import ConfigError, format_config, parse_args

EXIT_OK = 0
EXIT_CONFIG_ERROR = 2


def main(argv=None):
    """Запустить приложение; вернуть код завершения."""
    try:
        config = parse_args(argv)
    except ConfigError as error:
        print("Ошибка: %s" % error, file=sys.stderr)
        return EXIT_CONFIG_ERROR
    for line in format_config(config):
        print(line)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
