"""Источник зависимостей на основе репозитория NuGet."""

from depgraph.nuget import fetch_text, get_dependencies
from depgraph.versions import latest_version, lower_bound


class NuGetSource:
    """Выдаёт прямые зависимости пакетов, запрашивая nuspec-файлы.

    Версия каждого транзитивного пакета берётся из диапазона, с которым
    он встретился впервые (нижняя граница диапазона).
    """

    def __init__(self, repo, root, version, fetch=fetch_text):
        self.repo = repo
        self.fetch = fetch
        self.versions = {root.casefold(): version}
        self.names = {root.casefold(): root}
        self.cache = {}

    def dependencies(self, name):
        """Возвращает имена прямых зависимостей пакета."""
        key = name.casefold()
        if key not in self.cache:
            self.cache[key] = self.load(name)
        return self.cache[key]

    def load(self, name):
        """Запрашивает зависимости пакета и запоминает их версии."""
        version = self.versions[name.casefold()]
        found = get_dependencies(self.repo, name, version, self.fetch)
        return [self.register(item) for item in found]

    def register(self, dependency):
        """Запоминает имя и версию зависимости, возвращает каноническое имя."""
        key = dependency.name.casefold()
        if key not in self.versions:
            self.versions[key] = self.pick_version(dependency)
            self.names[key] = dependency.name
        return self.names[key]

    def pick_version(self, dependency):
        """Выбирает версию по диапазону; без границы - последнюю."""
        bound = lower_bound(dependency.version_range)
        if bound:
            return bound
        return latest_version(self.repo, dependency.name, self.fetch)
