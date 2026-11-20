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


class MainTest(unittest.TestCase):
    def test_chain(self):
        code, lines, _ = run_cli("-p", "A", "-t", "-r", example("chain.txt"))
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            lines, ["A -> B", "A -> C", "B -> D", "C -> E"]
        )

    def test_cycle(self):
        code, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("cycle.txt"), "-d", "4"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("C -> A", lines)
        self.assertIn("D -> D", lines)

    def test_depth_option(self):
        _, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("chain.txt"), "-d", "1"
        )
        self.assertEqual(lines, ["A -> B", "A -> C"])

    def test_filter_option(self):
        _, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("diamond.txt"), "-f", "D"
        )
        self.assertNotIn("B -> D", lines)
        self.assertIn("C -> X", lines)

    def test_unknown_package(self):
        code, _, err = run_cli("-p", "Z", "-t", "-r", example("chain.txt"))
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не найден", err)

    def test_bad_repo_file(self):
        bad = os.path.join(ROOT, "README.md")
        code, _, err = run_cli("-p", "A", "-t", "-r", bad)
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("Ошибка", err)


class ReverseMainTest(unittest.TestCase):
    def test_reverse_chain(self):
        code, lines, _ = run_cli(
            "-p", "E", "-t", "-r", example("diamond.txt"), "-R", "-d", "1"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(
            lines,
            ["Обратные зависимости пакета E:", "E <- D", "E <- X"],
        )

    def test_reverse_full(self):
        _, lines, _ = run_cli(
            "-p", "F", "-t", "-r", example("diamond.txt"), "-R", "-d", "10"
        )
        self.assertIn("C <- A", lines)
        self.assertIn("F <- E", lines)

    def test_reverse_cycle(self):
        _, lines, _ = run_cli(
            "-p", "D", "-t", "-r", example("cycle.txt"), "-R", "-d", "10"
        )
        self.assertIn("D <- D", lines)
        self.assertIn("A <- C", lines)

    def test_reverse_without_dependents(self):
        _, lines, _ = run_cli(
            "-p", "A", "-t", "-r", example("diamond.txt"), "-R"
        )
        self.assertEqual(lines[-1], "Обратных зависимостей нет")

    def test_reverse_needs_test_mode(self):
        code, _, err = run_cli("-p", "A", "-V", "1.0", "-R")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("тестовом режиме", err)
