"""Построение графа зависимостей рекурсивным обходом в глубину (DFS)."""

from dataclasses import dataclass


@dataclass
class Graph:
    """Граф зависимостей: корень и списки смежности развёрнутых узлов."""

    root: str
    edges: dict


class Walker:
    """Рекурсивный DFS с учётом глубины, фильтра имён и циклов."""

    def __init__(self, neighbors, max_depth, substring):
        self.neighbors = neighbors
        self.max_depth = max_depth
        self.substring = substring.casefold()
        self.edges = {}
        self.depths = {}

    def allowed(self, name):
        """Пакеты, в имени которых есть подстрока, не учитываются."""
        return not self.substring or self.substring not in name.casefold()

    def visit(self, node, depth):
        """Посещает узел; на предельной глубине узел не раскрывается."""
        self.depths[node] = depth
        self.edges[node] = []
        if depth >= self.max_depth:
            return
        found = self.neighbors(node)
        children = [item for item in dict.fromkeys(found) if self.allowed(item)]
        self.edges[node] = children
        for child in children:
            known = self.depths.get(child)
            if known is None or depth + 1 < known:
                self.visit(child, depth + 1)


def build_graph(root, neighbors, max_depth, substring=""):
    """Строит граф от корня функцией neighbors(имя) -> список имён.

    Цикл не приводит к зацикливанию: узел повторно раскрывается, только
    если до него нашёлся более короткий путь (глубина строго уменьшается).
    Ребро, замыкающее цикл, в графе сохраняется.
    """
    walker = Walker(neighbors, max_depth, substring)
    walker.visit(root, 0)
    return Graph(root, walker.edges)


def format_edges(graph):
    """Возвращает рёбра графа в виде строк ``A -> B``."""
    lines = [
        f"{parent} -> {child}"
        for parent, children in graph.edges.items()
        for child in children
    ]
    return lines or ["Зависимости не найдены"]
