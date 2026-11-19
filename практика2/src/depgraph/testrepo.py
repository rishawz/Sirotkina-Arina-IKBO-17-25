"""Тестовый репозиторий: граф зависимостей, описанный в текстовом файле.

Формат: одна строка на пакет, ``A: B C`` означает, что пакет A зависит
от B и C; ``D:`` - пакет без зависимостей. Имена пакетов - заглавные
латинские буквы. Пустые строки и строки, начинающиеся с ``#``,
пропускаются.
"""

import re

from depgraph.errors import SourceError

NAME_RE = re.compile(r"^[A-Z]+$")
SKIPPED_PREFIX = "#"
SEPARATOR = ":"


def parse_line(line, number):
    """Разбирает строку ``A: B C`` в пару (имя, список зависимостей)."""
    name, separator, rest = line.partition(SEPARATOR)
    if not separator:
        raise SourceError(f"строка {number}: нет разделителя '{SEPARATOR}'")
    names = [name.strip(), *rest.split()]
    for item in names:
        if not NAME_RE.match(item):
            raise SourceError(
                f"строка {number}: имя {item!r} должно состоять из "
                "заглавных латинских букв"
            )
    return names[0], list(dict.fromkeys(names[1:]))


def parse_repo(text):
    """Разбирает текст тестового репозитория в словарь имя -> зависимости."""
    repo = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(SKIPPED_PREFIX):
            continue
        name, children = parse_line(line, number)
        if name in repo:
            raise SourceError(f"строка {number}: пакет {name} описан дважды")
        repo[name] = children
    return repo


class FileSource:
    """Источник зависимостей на основе файла тестового репозитория."""

    def __init__(self, repo):
        self.repo = repo

    @classmethod
    def from_file(cls, path):
        """Читает и разбирает файл тестового репозитория."""
        try:
            with open(path, encoding="utf-8") as handle:
                return cls(parse_repo(handle.read()))
        except OSError as error:
            raise SourceError(
                f"не удалось прочитать {path}: {error}"
            ) from error

    def known(self, name):
        """Проверяет, что пакет упоминается в репозитории."""
        mentioned = {item for deps in self.repo.values() for item in deps}
        return name in self.repo or name in mentioned

    def dependencies(self, name):
        """Возвращает прямые зависимости пакета (пустой список для листа)."""
        return self.repo.get(name, [])
