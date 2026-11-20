"""Обратные зависимости: какие пакеты зависят от заданного."""


class ReverseSource:
    """Инвертированный индекс тестового репозитория."""

    def __init__(self, repo):
        self.dependents_of = {}
        for name, children in repo.items():
            for child in children:
                self.dependents_of.setdefault(child, []).append(name)

    def dependents(self, name):
        """Возвращает пакеты, напрямую зависящие от заданного."""
        return self.dependents_of.get(name, [])
