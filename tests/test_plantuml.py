import unittest

from depgraph.graph import Graph
from depgraph.plantuml import to_plantuml


class PlantUmlTest(unittest.TestCase):
    def test_graph(self):
        graph = Graph("A", {"A": ["B"], "B": []})
        self.assertEqual(
            to_plantuml(graph).splitlines(),
            [
                "@startuml",
                "title Зависимости пакета A",
                'rectangle "A" as n0 #LightBlue',
                'rectangle "B" as n1',
                "n0 --> n1",
                "@enduml",
            ],
        )

    def test_single_node(self):
        text = to_plantuml(Graph("A", {"A": []}))
        self.assertNotIn("-->", text)
        self.assertIn('rectangle "A" as n0', text)

    def test_cycle_edge(self):
        text = to_plantuml(Graph("A", {"A": ["B"], "B": ["A"]}))
        self.assertIn("n1 --> n0", text)

    def test_dotted_name(self):
        text = to_plantuml(Graph("Demo.App", {"Demo.App": []}))
        self.assertIn('"Demo.App"', text)
