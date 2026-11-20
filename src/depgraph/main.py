"""Точка входа приложения."""

import sys

from depgraph.cli import parse_args
from depgraph.errors import AppError, ConfigError
from depgraph.graph import build_graph, format_edges
from depgraph.nuget_source import NuGetSource
from depgraph.reverse import ReverseSource
from depgraph.testrepo import FileSource

EXIT_OK = 0
EXIT_ERROR = 2


def make_source(config):
    """Создаёт источник зависимостей согласно режиму работы."""
    if not config.test_mode:
        return NuGetSource(config.repo, config.package, config.version)
    source = FileSource.from_file(config.repo)
    if not source.known(config.package):
        raise ConfigError(
            f"пакет {config.package} не найден в {config.repo}"
        )
    return source


def run_reverse(config, source):
    """Выводит пакеты, которые зависят от заданного (прямо и косвенно).

    Обход тот же, что и на этапе 3 (build_graph), но соседями узла
    служат его обратные зависимости. Запись ``B <- A`` значит: A зависит
    от B.
    """
    neighbors = ReverseSource(source.repo).dependents
    graph = build_graph(
        config.package, neighbors, config.max_depth, config.substring
    )
    print(f"Обратные зависимости пакета {config.package}:")
    for line in format_edges(graph, "<-", "Обратных зависимостей нет"):
        print(line)


def run(config):
    """Строит граф зависимостей и выводит его рёбра."""
    source = make_source(config)
    if config.reverse:
        run_reverse(config, source)
        return
    graph = build_graph(
        config.package, source.dependencies, config.max_depth,
        config.substring,
    )
    for line in format_edges(graph):
        print(line)


def main(argv=None):
    """Запускает приложение и возвращает код завершения."""
    try:
        run(parse_args(argv))
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    except RecursionError:
        print("Ошибка: слишком глубокая цепочка зависимостей; "
              "уменьшите --max-depth", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
