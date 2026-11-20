import unittest

from depgraph.graph import build_graph, format_edges
from depgraph.reverse import ReverseSource
from depgraph.testrepo import parse_repo

DIAMOND = parse_repo("A: B C\nB: D\nC: D X\nD: E\nE: F\nX: E\nF:\n")
CYCLE = parse_repo("A: B\nB: C\nC: A\n")
BIG_DEPTH = 100


def reverse_edges(repo, root, depth=BIG_DEPTH, substring=""):
    neighbors = ReverseSource(repo).dependents
    return build_graph(root, neighbors, depth, substring).edges


class ReverseTest(unittest.TestCase):
    def test_index(self):
        index = ReverseSource(DIAMOND)
        self.assertEqual(index.dependents("D"), ["B", "C"])
        self.assertEqual(index.dependents("A"), [])

    def test_transitive_dependents(self):
        result = reverse_edges(DIAMOND, "E")
        self.assertEqual(result["E"], ["D", "X"])
        self.assertEqual(result["D"], ["B", "C"])
        self.assertEqual(result["C"], ["A"])
        self.assertEqual(result["A"], [])

    def test_depth_limit(self):
        result = reverse_edges(DIAMOND, "E", 1)
        self.assertEqual(result, {"E": ["D", "X"], "D": [], "X": []})

    def test_root_without_dependents(self):
        self.assertEqual(reverse_edges(DIAMOND, "A"), {"A": []})

    def test_cycle(self):
        result = reverse_edges(CYCLE, "A")
        self.assertEqual(result, {"A": ["C"], "C": ["B"], "B": ["A"]})

    def test_filter(self):
        result = reverse_edges(DIAMOND, "E", substring="X")
        self.assertNotIn("X", result)
        self.assertEqual(result["E"], ["D"])

    def test_format(self):
        graph = build_graph(
            "E", ReverseSource(DIAMOND).dependents, 1
        )
        self.assertEqual(
            format_edges(graph, "<-"), ["E <- D", "E <- X"]
        )
