"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

DEFAULT_REPO_URL = "https://index.crates.io"
DEFAULT_OUTPUT = "graph.svg"
SVG_SUFFIX = ".svg"
ALLOWED_SCHEMES = ("http", "https")
MAX_CRATE_NAME_LEN = 64
CRATE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
TEST_NAME_RE = re.compile(r"^[A-Z]+$")
TEST_FILTER_RE = re.compile(r"^[A-Z]*$")
WHITESPACE_RE = re.compile(r"\s")


class ConfigError(Exception):
    """Ошибка в параметрах командной строки."""


class _Parser(argparse.ArgumentParser):
    """Парсер, который сообщает об ошибках через ConfigError."""

    def error(self, message):
        """Бросить ConfigError вместо завершения процесса."""
        raise ConfigError(message)


@dataclass(frozen=True)
class Config:
    """Проверенные пользовательские параметры."""

    package: str
    repo: str
    test_mode: bool
    output: str
    ascii_tree: bool
    substring: str


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = _Parser(
        prog="depgraph",
        description="Визуализация графа зависимостей пакетов Cargo.",
    )
    parser.add_argument(
        "--package", required=True, help="имя анализируемого пакета"
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="URL репозитория (sparse-индекс) или, в тестовом режиме, "
        "путь к файлу графа; по умолчанию " + DEFAULT_REPO_URL,
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="тестовый режим: --repo - путь к файлу описания графа",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="имя файла SVG с графом (по умолчанию %s)" % DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="вывести зависимости в виде ASCII-дерева",
    )
    parser.add_argument(
        "--filter",
        default="",
        dest="substring",
        help="не учитывать пакеты, в имени которых есть подстрока",
    )
    return parser


def validate_package(name, test_mode):
    """Проверить имя пакета; вернуть его или бросить ConfigError."""
    if test_mode:
        if not TEST_NAME_RE.match(name):
            raise ConfigError(
                "в тестовом режиме имя пакета должно состоять "
                "из больших латинских букв: %r" % name
            )
        return name
    if len(name) > MAX_CRATE_NAME_LEN:
        raise ConfigError("слишком длинное имя пакета: %r" % name)
    if not CRATE_NAME_RE.match(name):
        raise ConfigError(
            "некорректное имя пакета Cargo (допустимы латинские буквы, "
            "цифры, '-' и '_', первый символ - буква или '_'): %r" % name
        )
    return name


def validate_url(url):
    """Проверить URL репозитория (http/https с именем хоста)."""
    if WHITESPACE_RE.search(url):
        raise ConfigError("URL содержит пробельные символы: %r" % url)
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ConfigError(
            "URL должен начинаться с http:// или https://: %r" % url
        )
    if not parsed.netloc:
        raise ConfigError("в URL не указан хост: %r" % url)
    return url.rstrip("/")


def validate_test_file(path):
    """Проверить, что путь указывает на читаемый файл."""
    if not os.path.exists(path):
        raise ConfigError("файл тестового репозитория не найден: %s" % path)
    if not os.path.isfile(path):
        raise ConfigError("путь не является файлом: %s" % path)
    if not os.access(path, os.R_OK):
        raise ConfigError("нет прав на чтение файла: %s" % path)
    return path


def validate_repo(repo, test_mode):
    """Проверить параметр репозитория с учётом режима работы."""
    if test_mode:
        if repo is None:
            raise ConfigError("в тестовом режиме нужно указать --repo")
        return validate_test_file(repo)
    return validate_url(DEFAULT_REPO_URL if repo is None else repo)


def validate_output(path):
    """Проверить имя выходного SVG-файла."""
    name = os.path.basename(path)
    if not name.lower().endswith(SVG_SUFFIX) or name.lower() == SVG_SUFFIX:
        raise ConfigError(
            "имя файла изображения должно иметь вид <имя>.svg: %r" % path
        )
    if os.path.isdir(path):
        raise ConfigError("путь указывает на каталог: %s" % path)
    parent = os.path.dirname(path) or "."
    if not os.path.isdir(parent):
        raise ConfigError("каталог для файла не существует: %s" % parent)
    return path


def validate_substring(substring, test_mode):
    """Проверить подстроку фильтрации (пустая - фильтр выключен)."""
    if WHITESPACE_RE.search(substring):
        raise ConfigError("подстрока содержит пробельные символы")
    if test_mode and not TEST_FILTER_RE.match(substring):
        raise ConfigError(
            "в тестовом режиме подстрока должна состоять "
            "из больших латинских букв: %r" % substring
        )
    return substring


def parse_args(argv=None):
    """Разобрать и проверить аргументы; вернуть Config."""
    args = build_parser().parse_args(argv)
    return Config(
        package=validate_package(args.package, args.test_mode),
        repo=validate_repo(args.repo, args.test_mode),
        test_mode=args.test_mode,
        output=validate_output(args.output),
        ascii_tree=args.ascii_tree,
        substring=validate_substring(args.substring, args.test_mode),
    )


def format_config(config):
    """Вернуть параметры в виде строк «ключ: значение»."""
    pairs = [
        ("package", config.package),
        ("repo", config.repo),
        ("test-mode", config.test_mode),
        ("output", config.output),
        ("ascii-tree", config.ascii_tree),
        ("filter", config.substring),
    ]
    return ["%s: %s" % (key, value) for key, value in pairs]
