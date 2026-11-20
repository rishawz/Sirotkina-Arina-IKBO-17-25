"""Вывод графа зависимостей в виде ASCII-дерева."""

BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
BLANK = "    "
REPEAT_MARK = " (*)"


def render_children(graph, node, prefix, expanded, lines):
    """Дописывает в lines потомков узла с отступом prefix."""
    children = graph.edges.get(node, [])
    for index, child in enumerate(children, start=1):
        is_last = index == len(children)
        lines.append(prefix + (LAST_BRANCH if is_last else BRANCH) + child)
        if not graph.edges.get(child):
            continue
        if child in expanded:
            lines[-1] += REPEAT_MARK
            continue
        expanded.add(child)
        render_children(
            graph, child, prefix + (BLANK if is_last else PIPE),
            expanded, lines,
        )


def render_tree(graph):
    """Возвращает строки ASCII-дерева, начиная с корневого пакета.

    Узел раскрывается один раз; повторное появление узла с зависимостями
    (общая зависимость или цикл) помечается ``(*)`` и не раскрывается.
    """
    lines = [graph.root]
    render_children(graph, graph.root, "", {graph.root}, lines)
    return lines
