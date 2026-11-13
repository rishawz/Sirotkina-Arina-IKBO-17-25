"""Тесты разбора и проверки параметров (этап 1)."""

import os
import tempfile
import unittest

from config import (
    DEFAULT_OUTPUT,
    DEFAULT_REPO_URL,
    ConfigError,
    format_config,
    parse_args,
)


class ConfigTestCase(unittest.TestCase):
    """Базовый класс с временным файлом тестового репозитория."""

    def setUp(self):
        """Создать временный каталог и файл графа."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.graph = os.path.join(self.tmp.name, "graph.txt")
        with open(self.graph, "w", encoding="utf-8") as handle:
            handle.write("A: B\nB:\n")

    def assertRejected(self, argv):
        """Проверить, что аргументы отвергаются с ConfigError."""
        with self.assertRaises(ConfigError):
            parse_args(argv)


class ValidConfigTests(ConfigTestCase):
    """Корректные наборы параметров."""

    def test_defaults(self):
        """Значения по умолчанию в обычном режиме."""
        config = parse_args(["--package", "serde"])
        self.assertEqual(config.repo, DEFAULT_REPO_URL)
        self.assertEqual(config.output, DEFAULT_OUTPUT)
        self.assertFalse(config.test_mode)
        self.assertFalse(config.ascii_tree)
        self.assertEqual(config.substring, "")

    def test_all_options(self):
        """Все параметры заданы явно."""
        out = os.path.join(self.tmp.name, "out.svg")
        config = parse_args([
            "--package", "A", "--repo", self.graph, "--test-mode",
            "--output", out, "--ascii-tree", "--filter", "X",
        ])
        self.assertEqual(config.package, "A")
        self.assertEqual(config.repo, self.graph)
        self.assertTrue(config.test_mode and config.ascii_tree)
        self.assertEqual(config.output, out)
        self.assertEqual(config.substring, "X")

    def test_custom_url_trailing_slash_removed(self):
        """Завершающий '/' в URL отбрасывается."""
        config = parse_args(
            ["--package", "serde", "--repo", "http://localhost:8000/"]
        )
        self.assertEqual(config.repo, "http://localhost:8000")

    def test_format_config(self):
        """Вывод в формате «ключ: значение»."""
        config = parse_args(["--package", "serde", "--filter", "sys"])
        lines = format_config(config)
        self.assertIn("package: serde", lines)
        self.assertIn("filter: sys", lines)
        self.assertIn("test-mode: False", lines)


class InvalidConfigTests(ConfigTestCase):
    """Ошибочные параметры должны отвергаться."""

    def test_missing_package(self):
        """Не указан обязательный --package."""
        self.assertRejected([])

    def test_missing_value(self):
        """У опции нет значения."""
        self.assertRejected(["--package"])

    def test_unknown_option(self):
        """Неизвестная опция."""
        self.assertRejected(["--package", "serde", "--depth", "3"])

    def test_flag_with_value(self):
        """Флаг не принимает значение (неверный тип значения)."""
        self.assertRejected(["--package", "serde", "--ascii-tree", "yes"])

    def test_bad_crate_names(self):
        """Некорректные имена пакетов Cargo."""
        for name in ("", "1serde", "se rde", "se/rde", "a" * 65, "сердэ"):
            with self.subTest(name=name):
                self.assertRejected(["--package", name])

    def test_bad_test_package_names(self):
        """В тестовом режиме имя - только большие латинские буквы."""
        for name in ("a", "A1", "AB-C", ""):
            with self.subTest(name=name):
                self.assertRejected(
                    ["--package", name, "--test-mode", "--repo", self.graph]
                )

    def test_bad_urls(self):
        """Некорректные URL репозитория."""
        for url in ("index.crates.io", "ftp://host/x", "https://", "http:/x",
                    "https://a b"):
            with self.subTest(url=url):
                self.assertRejected(["--package", "serde", "--repo", url])

    def test_test_mode_requires_repo(self):
        """В тестовом режиме без --repo - ошибка."""
        self.assertRejected(["--package", "A", "--test-mode"])

    def test_test_mode_missing_file(self):
        """Файл тестового репозитория не существует."""
        missing = os.path.join(self.tmp.name, "nope.txt")
        self.assertRejected(
            ["--package", "A", "--test-mode", "--repo", missing]
        )

    def test_test_mode_directory_instead_of_file(self):
        """Вместо файла указан каталог."""
        self.assertRejected(
            ["--package", "A", "--test-mode", "--repo", self.tmp.name]
        )

    def test_bad_output_names(self):
        """Некорректное имя выходного файла."""
        bad_dir = os.path.join(self.tmp.name, "missing", "g.svg")
        for out in ("graph.png", "graph", ".svg", bad_dir, self.tmp.name):
            with self.subTest(out=out):
                self.assertRejected(["--package", "serde", "--output", out])

    def test_filter_with_whitespace(self):
        """Пробелы в подстроке фильтрации."""
        self.assertRejected(["--package", "serde", "--filter", "a b"])

    def test_test_mode_filter_lowercase(self):
        """В тестовом режиме подстрока - большие латинские буквы."""
        self.assertRejected([
            "--package", "A", "--test-mode", "--repo", self.graph,
            "--filter", "x",
        ])


if __name__ == "__main__":
    unittest.main()
