import contextlib
import io
import os
import unittest

from depgraph.main import EXIT_ERROR, EXIT_OK, main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "examples")


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue().splitlines(), err.getvalue()


def example(name):
    return os.path.join(EXAMPLES, name)


def arrows(lines):
    return [line for line in lines if "-->" in line]


class MainTest(unittest.TestCase):
    def test_chain_plantuml(self):
        code, lines, _ = run_cli("-p", "A", "-t", "-r", example("chain.txt"))
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(lines[0], "@startuml")
        self.assertEqual(lines[-1], "@enduml")
        self.assertEqual(
            arrows(lines), ["n0 --> n1", "n0 --> n3", "n1 --> n2", "n3 --> n4"]
        )

    def test_no_tree_by_default(self):
        _, lines, _ = run_cli("-p", "A", "-t", "-r", example("chain.txt"))
        self.assertNotIn("ASCII-дерево зависимостей:", lines)

    def test_ascii_tree(self):
        code, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("chain.txt"), "-a"
        )
        self.assertEqual(code, EXIT_OK)
        start = lines.index("ASCII-дерево зависимостей:")
        self.assertEqual(
            lines[start + 1:],
            ["A", "├── B", "│   └── D", "└── C", "    └── E"],
        )

    def test_cycle(self):
        code, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("cycle.txt"), "-d", "4", "-a"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("        ├── A (*)", lines)

    def test_depth_option(self):
        _, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("chain.txt"), "-d", "1"
        )
        self.assertEqual(arrows(lines), ["n0 --> n1", "n0 --> n2"])

    def test_filter_option(self):
        _, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("diamond.txt"), "-f", "D", "-a"
        )
        self.assertNotIn('rectangle "D" as n2', lines)
        self.assertTrue(any("X" in line for line in lines))

    def test_unknown_package(self):
        code, _, err = run_cli("-p", "Z", "-t", "-r", example("chain.txt"))
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не найден", err)

    def test_bad_repo_file(self):
        bad = os.path.join(ROOT, "README.md")
        code, _, err = run_cli("-p", "A", "-t", "-r", bad)
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("Ошибка", err)

    def test_reverse_option_is_gone(self):
        with self.assertRaises(SystemExit):
            run_cli("-p", "A", "-t", "-r", example("chain.txt"), "-R")
