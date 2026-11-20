"""Разбор опций командной строки."""

import argparse

from depgraph.config import DEFAULT_MAX_DEPTH, build_config


def add_source_options(parser):
    """Добавляет опции, описывающие источник данных."""
    parser.add_argument(
        "-p", "--package", required=True, help="имя анализируемого пакета"
    )
    parser.add_argument(
        "-r", "--repo",
        help="URL репозитория NuGet (flat container) или путь к файлу "
        "тестового репозитория",
    )
    parser.add_argument(
        "-t", "--test-mode", action="store_true",
        help="работать с файлом тестового репозитория вместо URL",
    )
    parser.add_argument(
        "-V", "--version", help="версия пакета (например, 13.0.3)"
    )


def add_analysis_options(parser):
    """Добавляет опции, управляющие анализом и выводом."""
    parser.add_argument(
        "-a", "--ascii-tree", action="store_true",
        help="выводить зависимости в формате ASCII-дерева",
    )
    parser.add_argument(
        "-d", "--max-depth", type=int, default=DEFAULT_MAX_DEPTH,
        help="максимальная глубина анализа (по умолчанию %(default)s)",
    )
    parser.add_argument(
        "-f", "--substring", default="",
        help="не учитывать пакеты, в имени которых есть эта подстрока",
    )


def build_parser():
    """Создаёт разборщик командной строки."""
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Визуализация графа зависимостей пакетов NuGet.",
    )
    add_source_options(parser)
    add_analysis_options(parser)
    return parser


def parse_args(argv=None):
    """Разбирает аргументы и возвращает проверенную конфигурацию."""
    return build_config(build_parser().parse_args(argv))
