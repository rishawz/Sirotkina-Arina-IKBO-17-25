import unittest

from depgraph.graph import Graph
from depgraph.tree import render_tree


class TreeTest(unittest.TestCase):
    def test_single_node(self):
        self.assertEqual(render_tree(Graph("A", {"A": []})), ["A"])

    def test_branches(self):
        graph = Graph(
            "A", {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
        )
        self.assertEqual(
            render_tree(graph),
            ["A", "├── B", "│   └── D", "└── C"],
        )

    def test_shared_dependency_marked_once(self):
        graph = Graph(
            "A",
            {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["E"], "E": []},
        )
        self.assertEqual(
            render_tree(graph),
            ["A", "├── B", "│   └── D", "│       └── E",
             "└── C", "    └── D (*)"],
        )

    def test_cycle(self):
        graph = Graph("A", {"A": ["B"], "B": ["A"]})
        self.assertEqual(render_tree(graph), ["A", "└── B", "    └── A (*)"])

    def test_leaf_repeated_not_marked(self):
        graph = Graph("A", {"A": ["B", "C"], "B": ["L"], "C": ["L"], "L": []})
        self.assertEqual(render_tree(graph)[-1], "    └── L")
