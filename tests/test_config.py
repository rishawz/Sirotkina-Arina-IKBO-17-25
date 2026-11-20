import os
import tempfile
import unittest

from depgraph.cli import parse_args
from depgraph.config import DEFAULT_MAX_DEPTH, DEFAULT_REPO_URL
from depgraph.errors import ConfigError


class ConfigTest(unittest.TestCase):
    def test_defaults(self):
        config = parse_args(["-p", "Newtonsoft.Json", "-V", "13.0.3"])
        self.assertEqual(config.repo, DEFAULT_REPO_URL)
        self.assertEqual(config.max_depth, DEFAULT_MAX_DEPTH)
        self.assertEqual(config.substring, "")
        self.assertFalse(config.ascii_tree)

    def test_all_options(self):
        config = parse_args([
            "-p", "A.B", "-r", "https://example.org/v3/", "-V", "1.0.0-rc.1",
            "-a", "-d", "5", "-f", "Test",
        ])
        self.assertEqual(config.max_depth, 5)
        self.assertEqual(config.substring, "Test")
        self.assertTrue(config.ascii_tree)

    def test_version_required(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "Serilog"])

    def test_bad_version(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "Serilog", "-V", "abc"])

    def test_bad_package(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "bad name!", "-V", "1.0"])

    def test_bad_url(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "Serilog", "-V", "1.0", "-r", "ftp://x"])

    def test_negative_depth(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "Serilog", "-V", "1.0", "-d", "-1"])

    def test_non_integer_depth(self):
        with self.assertRaises(SystemExit):
            parse_args(["-p", "Serilog", "-V", "1.0", "-d", "many"])

    def test_test_mode_requires_repo(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "A", "-t"])

    def test_test_mode_missing_file(self):
        with self.assertRaises(ConfigError):
            parse_args(["-p", "A", "-t", "-r", "/no/such/file.txt"])

    def test_test_mode_lowercase_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "repo.txt")
            open(path, "w").close()
            with self.assertRaises(ConfigError):
                parse_args(["-p", "a", "-t", "-r", path])

    def test_test_mode_ok_without_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "repo.txt")
            open(path, "w").close()
            config = parse_args(["-p", "A", "-t", "-r", path])
            self.assertEqual(config.version, "")
            self.assertTrue(config.test_mode)
