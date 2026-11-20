import os
import tempfile
import unittest

from depgraph.errors import SourceError
from depgraph.testrepo import FileSource, parse_repo


class ParseRepoTest(unittest.TestCase):
    def test_basic(self):
        repo = parse_repo("# c\n\nA: B C\nB:\n")
        self.assertEqual(repo, {"A": ["B", "C"], "B": []})

    def test_duplicates_in_line_removed(self):
        self.assertEqual(parse_repo("A: B B\n"), {"A": ["B"]})

    def test_no_separator(self):
        with self.assertRaises(SourceError):
            parse_repo("A B\n")

    def test_lowercase_name(self):
        with self.assertRaises(SourceError):
            parse_repo("A: b\n")

    def test_duplicate_package(self):
        with self.assertRaises(SourceError):
            parse_repo("A: B\nA: C\n")


class FileSourceTest(unittest.TestCase):
    def test_known_and_leaf(self):
        source = FileSource({"A": ["B"]})
        self.assertTrue(source.known("B"))
        self.assertFalse(source.known("Z"))
        self.assertEqual(source.dependencies("B"), [])

    def test_from_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "r.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("A: B\n")
            self.assertEqual(FileSource.from_file(path).repo, {"A": ["B"]})

    def test_from_file_missing(self):
        with self.assertRaises(SourceError):
            FileSource.from_file("/no/such/file")
