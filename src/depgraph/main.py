"""Точка входа приложения."""

import sys

from depgraph.cli import parse_args
from depgraph.errors import AppError, ConfigError
from depgraph.graph import build_graph
from depgraph.nuget_source import NuGetSource
from depgraph.plantuml import to_plantuml
from depgraph.testrepo import FileSource
from depgraph.tree import render_tree

EXIT_OK = 0
EXIT_ERROR = 2
TREE_TITLE = "ASCII-дерево зависимостей:"


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


def run(config):
    """Строит граф, выводит описание PlantUML и, по запросу, дерево."""
    source = make_source(config)
    graph = build_graph(
        config.package, source.dependencies, config.max_depth,
        config.substring,
    )
    print(to_plantuml(graph))
    if config.ascii_tree:
        print()
        print(TREE_TITLE)
        for line in render_tree(graph):
            print(line)


def main(argv=None):
    """Запускает приложение и возвращает код завершения."""
    try:
        run(parse_args(argv))
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    except RecursionError:
        print("Ошибка: слишком глубокая цепочка зависимостей, "
              "уменьшите --max-depth", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
