"""Текстовое представление графа зависимостей на языке PlantUML."""

ROOT_COLOR = "#LightBlue"


def quote(name):
    """Возвращает имя узла в кавычках для PlantUML."""
    return '"' + name.replace('"', '\\"') + '"'


def to_plantuml(graph):
    """Формирует диаграмму PlantUML: узлы-прямоугольники и стрелки.

    Стрелка ``A --> B`` означает, что пакет A зависит от пакета B.
    Корневой пакет выделен цветом.
    """
    aliases = {name: f"n{index}" for index, name in enumerate(graph.edges)}
    lines = ["@startuml", f"title Зависимости пакета {graph.root}"]
    for name, alias in aliases.items():
        color = f" {ROOT_COLOR}" if name == graph.root else ""
        lines.append(f"rectangle {quote(name)} as {alias}{color}")
    for parent, children in graph.edges.items():
        for child in children:
            lines.append(f"{aliases[parent]} --> {aliases[child]}")
    lines.append("@enduml")
    return "\n".join(lines)
