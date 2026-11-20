"""Конфигурация приложения и проверка параметров."""

import os
import re
from dataclasses import dataclass

from depgraph.errors import ConfigError

DEFAULT_REPO_URL = "https://api.nuget.org/v3-flatcontainer/"
DEFAULT_MAX_DEPTH = 3
MIN_DEPTH = 0
PACKAGE_ID_RE = re.compile(r"^[A-Za-z0-9_]+([.\-][A-Za-z0-9_]+)*$")
TEST_NAME_RE = re.compile(r"^[A-Z]+$")
VERSION_RE = re.compile(
    r"^\d+(\.\d+){0,3}(-[0-9A-Za-z.\-]+)?(\+[0-9A-Za-z.\-]+)?$"
)
URL_SCHEMES = ("http://", "https://")


@dataclass(frozen=True)
class Config:
    """Параметры, настраиваемые пользователем."""

    package: str
    repo: str
    test_mode: bool
    version: str
    ascii_tree: bool
    max_depth: int
    substring: str
    reverse: bool = False

    def as_pairs(self):
        """Возвращает параметры в виде списка пар ключ-значение."""
        return [
            ("package", self.package),
            ("repo", self.repo),
            ("test_mode", self.test_mode),
            ("version", self.version),
            ("ascii_tree", self.ascii_tree),
            ("max_depth", self.max_depth),
            ("substring", self.substring),
            ("reverse", self.reverse),
        ]


def check_package(package, test_mode):
    """Проверяет имя пакета для выбранного режима работы."""
    if test_mode and not TEST_NAME_RE.match(package):
        raise ConfigError(
            "в тестовом режиме имя пакета - заглавные латинские "
            f"буквы (например, A), получено: {package!r}"
        )
    if not test_mode and not PACKAGE_ID_RE.match(package):
        raise ConfigError(f"недопустимое имя пакета NuGet: {package!r}")
    return package


def check_repo(repo, test_mode):
    """Проверяет URL репозитория или путь к файлу тестового репозитория."""
    if repo is None:
        if test_mode:
            raise ConfigError(
                "в тестовом режиме нужно указать файл через --repo"
            )
        return DEFAULT_REPO_URL
    if test_mode:
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        return repo
    if not repo.startswith(URL_SCHEMES):
        raise ConfigError(
            f"URL репозитория должен начинаться с http:// или https://: "
            f"{repo!r}"
        )
    return repo


def check_version(version, test_mode):
    """Проверяет версию пакета (в тестовом режиме она не нужна)."""
    if version is None:
        if test_mode:
            return ""
        raise ConfigError("версия пакета обязательна (опция --version)")
    if not VERSION_RE.match(version):
        raise ConfigError(f"некорректная версия пакета: {version!r}")
    return version


def check_depth(depth):
    """Проверяет максимальную глубину анализа."""
    if depth < MIN_DEPTH:
        raise ConfigError(
            f"глубина анализа не может быть меньше {MIN_DEPTH}: {depth}"
        )
    return depth


def check_reverse(reverse, test_mode):
    """Обратные зависимости требуют полного индекса - тестового репозитория."""
    if reverse and not test_mode:
        raise ConfigError(
            "обратные зависимости доступны только в тестовом режиме: "
            "NuGet не отдаёт индекс «кто зависит от пакета», "
            "добавьте --test-mode"
        )
    return reverse


def build_config(args):
    """Создаёт проверенную конфигурацию из разобранных опций."""
    test_mode = args.test_mode
    return Config(
        package=check_package(args.package, test_mode),
        repo=check_repo(args.repo, test_mode),
        test_mode=test_mode,
        version=check_version(args.version, test_mode),
        ascii_tree=args.ascii_tree,
        max_depth=check_depth(args.max_depth),
        substring=args.substring,
        reverse=check_reverse(args.reverse, test_mode),
    )
