import functools
import http.server
import os
import threading
import unittest
import urllib.request

from depgraph.errors import SourceError
from depgraph.nuget import (
    Dependency, get_dependencies, nuspec_url, parse_nuspec,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DIR = os.path.join(ROOT, "examples", "mock-nuget")

SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>Pkg</id>
    <dependencies>
      <group targetFramework="net6.0">
        <dependency id="One" version="1.0.0" />
        <dependency id="Two" version="[2.0, )" />
      </group>
      <group targetFramework="net48">
        <dependency id="one" version="0.5.0" />
        <dependency id="Three" />
      </group>
    </dependencies>
  </metadata>
</package>
"""


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class ParseTest(unittest.TestCase):
    def test_union_of_groups_keeps_first(self):
        found = parse_nuspec(SAMPLE)
        self.assertEqual(
            found,
            [
                Dependency("One", "1.0.0"),
                Dependency("Two", "[2.0, )"),
                Dependency("Three", ""),
            ],
        )

    def test_no_dependencies(self):
        text = "<package><metadata><id>X</id></metadata></package>"
        self.assertEqual(parse_nuspec(text), [])

    def test_broken_xml(self):
        with self.assertRaises(SourceError):
            parse_nuspec("<package>")

    def test_url_is_lowercase(self):
        self.assertEqual(
            nuspec_url("https://h/v3/", "Newtonsoft.Json", "13.0.3"),
            "https://h/v3/newtonsoft.json/13.0.3/newtonsoft.json.nuspec",
        )

    def test_get_dependencies_uses_fetch(self):
        urls = []

        def fake(url):
            urls.append(url)
            return SAMPLE

        found = get_dependencies("https://h", "Pkg", "1.0", fake)
        self.assertEqual(len(found), 3)
        self.assertEqual(urls, ["https://h/pkg/1.0/pkg.nuspec"])


class HttpTest(unittest.TestCase):
    def setUp(self):
        self.server_closed = False
        handler = functools.partial(QuietHandler, directory=MOCK_DIR)
        self.server = http.server.HTTPServer(("127.0.0.1", 0), handler)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}/"
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()
        no_proxy = urllib.request.ProxyHandler({})
        urllib.request.install_opener(urllib.request.build_opener(no_proxy))

    def tearDown(self):
        if not self.server_closed:
            self.server.shutdown()
            self.server.server_close()
        urllib.request.install_opener(None)

    def test_direct_dependencies_over_http(self):
        found = get_dependencies(self.base, "Demo.App", "1.0.0")
        names = [item.name for item in found]
        self.assertEqual(names, ["Demo.Core", "Demo.Logging", "Demo.Compat"])

    def test_missing_package(self):
        with self.assertRaises(SourceError):
            get_dependencies(self.base, "Demo.Nope", "1.0.0")

    def test_unreachable_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_closed = True
        with self.assertRaises(SourceError):
            get_dependencies(self.base, "Demo.App", "1.0.0")
