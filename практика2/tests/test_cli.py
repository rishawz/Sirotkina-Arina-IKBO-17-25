"""Тесты запуска приложения как консольной программы (этап 1)."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "src", "main.py")
EXIT_OK = 0
EXIT_CONFIG_ERROR = 2


def run_cli(*args):
    """Запустить main.py; вернуть CompletedProcess."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, MAIN, *args],
        capture_output=True, text=True, env=env, check=False,
    )


class CliTests(unittest.TestCase):
    """Проверка кодов завершения и вывода."""

    def test_valid_run_prints_key_values(self):
        """Корректный запуск выводит все параметры."""
        result = run_cli("--package", "serde", "--filter", "sys")
        self.assertEqual(result.returncode, EXIT_OK)
        self.assertIn("package: serde", result.stdout)
        self.assertIn("repo: https://index.crates.io", result.stdout)
        self.assertIn("test-mode: False", result.stdout)
        self.assertIn("output: graph.svg", result.stdout)
        self.assertIn("ascii-tree: False", result.stdout)
        self.assertIn("filter: sys", result.stdout)

    def test_test_mode_run(self):
        """Корректный запуск в тестовом режиме."""
        with tempfile.NamedTemporaryFile("w", suffix=".txt") as handle:
            handle.write("A:\n")
            handle.flush()
            result = run_cli(
                "--package", "A", "--test-mode", "--repo", handle.name
            )
        self.assertEqual(result.returncode, EXIT_OK)
        self.assertIn("test-mode: True", result.stdout)

    def test_error_goes_to_stderr(self):
        """Ошибка: код 2, сообщение в stderr, stdout пуст."""
        result = run_cli("--package", "serde", "--repo", "bad-url")
        self.assertEqual(result.returncode, EXIT_CONFIG_ERROR)
        self.assertIn("Ошибка:", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_missing_package_error(self):
        """Без --package программа сообщает об ошибке."""
        result = run_cli()
        self.assertEqual(result.returncode, EXIT_CONFIG_ERROR)
        self.assertIn("--package", result.stderr)


if __name__ == "__main__":
    unittest.main()
