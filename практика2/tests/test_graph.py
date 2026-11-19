import unittest

from depgraph.graph import build_graph
from depgraph.testrepo import FileSource, parse_repo

CYCLE = parse_repo("A: B\nB: C\nC: A D\nD: D\n")
DIAMOND = parse_repo("A: B C\nB: D\nC: D X\nD: E\nE: F\nX: E\nF:\n")
BIG_DEPTH = 100


def edges(repo, root, depth, substring=""):
    source = FileSource(repo)
    graph = build_graph(root, source.dependencies, depth, substring)
    return graph.edges


class DfsTest(unittest.TestCase):
    def test_full_graph(self):
        result = edges(DIAMOND, "A", BIG_DEPTH)
        self.assertEqual(
            result,
            {"A": ["B", "C"], "B": ["D"], "D": ["E"], "E": ["F"], "F": [],
             "C": ["D", "X"], "X": ["E"]},
        )

    def test_depth_zero_is_root_only(self):
        self.assertEqual(edges(DIAMOND, "A", 0), {"A": []})

    def test_depth_one(self):
        self.assertEqual(
            edges(DIAMOND, "A", 1), {"A": ["B", "C"], "B": [], "C": []}
        )

    def test_depth_limits_nodes(self):
        result = edges(DIAMOND, "A", 2)
        self.assertEqual(result["D"], [])
        self.assertEqual(result["X"], [])
        self.assertNotIn("E", result)

    def test_node_reached_shorter_later_is_expanded(self):
        repo = parse_repo("A: B C\nB: P\nP: T\nC: T\nT: U\nU:\n")
        result = edges(repo, "A", 3)
        self.assertEqual(result["T"], ["U"])

    def test_cycle_terminates_and_keeps_closing_edge(self):
        result = edges(CYCLE, "A", BIG_DEPTH)
        self.assertEqual(result["C"], ["A", "D"])
        self.assertEqual(result["D"], ["D"])
        self.assertEqual(set(result), {"A", "B", "C", "D"})

    def test_substring_filter(self):
        result = edges(DIAMOND, "A", BIG_DEPTH, "D")
        self.assertNotIn("D", result)
        self.assertEqual(result["C"], ["X"])
        self.assertEqual(result["X"], ["E"])

    def test_filter_is_case_insensitive(self):
        result = edges(DIAMOND, "A", BIG_DEPTH, "x")
        self.assertNotIn("X", result)
