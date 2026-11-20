import json
import unittest

from depgraph.errors import SourceError
from depgraph.nuget_source import NuGetSource
from depgraph.versions import latest_version, lower_bound

NUSPECS = {
    "https://h/a/1.0.0/a.nuspec": (
        '<package><metadata><dependencies><group>'
        '<dependency id="B" version="[1.5.0, )"/>'
        '<dependency id="C"/></group></dependencies></metadata></package>'
    ),
    "https://h/b/1.5.0/b.nuspec": (
        '<package><metadata><dependencies><group>'
        '<dependency id="a" version="1.0.0"/></group>'
        '</dependencies></metadata></package>'
    ),
    "https://h/c/3.0.0/c.nuspec": "<package><metadata/></package>",
    "https://h/c/index.json": json.dumps(
        {"versions": ["1.0.0", "3.0.0", "4.0.0-beta"]}
    ),
}


def fake_fetch(url):
    if url not in NUSPECS:
        raise SourceError(f"not found: {url}")
    return NUSPECS[url]


class LowerBoundTest(unittest.TestCase):
    def test_variants(self):
        cases = {
            "1.0.0": "1.0.0",
            "[1.0.0, )": "1.0.0",
            "[1.0.0]": "1.0.0",
            "(1.0, 2.0)": "1.0",
            "": None,
            "(, 1.0]": None,
            "1.*": None,
        }
        for text, expected in cases.items():
            self.assertEqual(lower_bound(text), expected, text)


class LatestVersionTest(unittest.TestCase):
    def test_prefers_stable(self):
        self.assertEqual(latest_version("https://h", "C", fake_fetch), "3.0.0")

    def test_only_prerelease(self):
        def fetch(url):
            return json.dumps({"versions": ["1.0.0-a", "1.0.0-b"]})

        self.assertEqual(latest_version("https://h", "C", fetch), "1.0.0-b")

    def test_empty_and_broken(self):
        for body in ('{"versions": []}', "not json", "{}"):
            with self.assertRaises(SourceError):
                latest_version("https://h", "C", lambda url, b=body: b)


class NuGetSourceTest(unittest.TestCase):
    def test_transitive_versions(self):
        source = NuGetSource("https://h", "A", "1.0.0", fake_fetch)
        self.assertEqual(source.dependencies("A"), ["B", "C"])
        self.assertEqual(source.versions["b"], "1.5.0")
        self.assertEqual(source.versions["c"], "3.0.0")
        self.assertEqual(source.dependencies("B"), ["A"])
        self.assertEqual(source.dependencies("C"), [])

    def test_missing_dependency_package(self):
        source = NuGetSource("https://h", "A", "1.0.0", fake_fetch)
        source.dependencies("A")
        source.versions["b"] = "9.9.9"
        with self.assertRaises(SourceError):
            source.load("B")
