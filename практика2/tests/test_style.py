"""Проверка кода на ограничения методички (раздел «Перечень нарушений»)."""

import ast
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_LINE = 80
MAX_FILE_LINES = 1000
MAX_FUNC_LINES = 40
MAX_ARGS = 7
MAX_COMPLEXITY = 10
ALLOWED_COMPARE_NUMBERS = (0,)
BRANCH_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler, ast.IfExp,
    ast.comprehension, ast.Assert,
)


def python_files():
    """Вернуть пути всех .py-файлов в src и tests."""
    found = []
    for folder in ("src", "tests"):
        for base, _, names in os.walk(os.path.join(ROOT, folder)):
            found += [os.path.join(base, n) for n in names
                      if n.endswith(".py")]
    return sorted(found)


def functions(tree):
    """Вернуть все определения функций и методов."""
    return [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def complexity(func):
    """Приближённая цикломатическая сложность функции."""
    total = 1
    for node in ast.walk(func):
        if isinstance(node, BRANCH_NODES):
            total += 1
        elif isinstance(node, ast.BoolOp):
            total += len(node.values) - 1
    return total


def arg_count(func):
    """Число аргументов функции."""
    args = func.args
    names = args.posonlyargs + args.args + args.kwonlyargs
    return len(names) + bool(args.vararg) + bool(args.kwarg)


def magic_numbers(tree):
    """Найти числовые литералы в сравнениях (кроме разрешённых)."""
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for part in [node.left, *node.comparators]:
            if (isinstance(part, ast.Constant)
                    and isinstance(part.value, (int, float))
                    and not isinstance(part.value, bool)
                    and part.value not in ALLOWED_COMPARE_NUMBERS):
                bad.append(node.lineno)
    return bad


class StyleTests(unittest.TestCase):
    """Автоматическая проверка правил оформления кода."""

    def setUp(self):
        """Прочитать и разобрать все файлы проекта."""
        self.sources = {}
        for path in python_files():
            with open(path, encoding="utf-8") as handle:
                self.sources[path] = handle.read()

    def test_files_found(self):
        """Проверка действительно охватывает файлы."""
        self.assertTrue(self.sources)

    def test_line_and_file_length(self):
        """Строки не длиннее 80, файлы не больше 1000 строк."""
        for path, text in self.sources.items():
            lines = text.splitlines()
            self.assertLessEqual(len(lines), MAX_FILE_LINES, path)
            for number, line in enumerate(lines, 1):
                self.assertLessEqual(len(line), MAX_LINE, (path, number))

    def test_function_rules(self):
        """Длина, число аргументов, сложность, docstring."""
        for path, text in self.sources.items():
            self.assertTrue(ast.get_docstring(ast.parse(text)), path)
            for func in functions(ast.parse(text)):
                where = (path, func.name)
                length = func.end_lineno - func.lineno + 1
                self.assertLessEqual(length, MAX_FUNC_LINES, where)
                self.assertLessEqual(arg_count(func), MAX_ARGS, where)
                self.assertLessEqual(complexity(func), MAX_COMPLEXITY, where)
                self.assertTrue(ast.get_docstring(func), where)

    def test_no_magic_numbers_in_comparisons(self):
        """Нет числовых литералов в сравнениях."""
        for path, text in self.sources.items():
            self.assertEqual(magic_numbers(ast.parse(text)), [], path)

    def test_no_service_files(self):
        """В рабочем дереве нет служебных файлов Python."""
        for base, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d != ".git"]
            self.assertNotIn("__pycache__", dirs, base)
            self.assertFalse([n for n in names if n.endswith(".pyc")])


if __name__ == "__main__":
    unittest.main()
