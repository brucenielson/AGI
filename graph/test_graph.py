from unittest import TestCase
from graph.graph import Graph, Edge, Vertex


class TestGraph(TestCase):
    def test_create_vertex(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        self.assertEqual(bobby, graph.vertices[0])
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)

    def test_register_vertex(self):
        vertex = Vertex('Bobby')
        graph = Graph()
        graph._register_vertex(vertex)
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        graph._register_vertex(vertex)
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)

    def test_register_edge(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        # Verify vertices and no edges
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        # Register an edge
        edge = Edge(timmy, name='friend', value=2.0)
        bobby.relate(edge)
        graph._register_edge(edge)
        # Verify vertices again - but now we have one edge
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual(2.0, bobby.edges[0].value)
        # We didn't actually link these vertices so no edge here
        self.assertEqual(0, len(timmy.edges))
        # Attempt to register an edge twice
        graph._register_edge(edge)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual(0, len(timmy.edges))
        self.assertEqual('Timmy', bobby.edges[0].vertex.name)

    def test_link_vertices(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        # Verify vertices and no edges
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(2, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual(1, len(bobby.edges))
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual(1.0, bobby.edges[0].value)
        self.assertEqual(1, len(timmy.edges))
        self.assertEqual('friend', timmy.edges[0].name)
        self.assertEqual(1.0, timmy.edges[0].value)
        self.assertEqual(1, len(timmy.edges))
        self.assertEqual('Timmy', bobby.edges[0].vertex.name)
        self.assertEqual('Bobby', timmy.edges[0].vertex.name)
        # Attempt to add a second edge (which is allowed)
        graph.link_vertices(bobby, timmy, 'roommate', two_way=True)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(4, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual(2, len(bobby.edges))
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual('roommate', bobby.edges[1].name)
        self.assertEqual(2, len(timmy.edges))
        self.assertEqual('friend', timmy.edges[0].name)
        self.assertEqual('roommate', timmy.edges[1].name)
        self.assertEqual(2, len(timmy.edges))
        self.assertEqual('Timmy', bobby.edges[0].vertex.name)
        self.assertEqual('Bobby', timmy.edges[0].vertex.name)
        self.assertEqual('Timmy', bobby.edges[1].vertex.name)
        self.assertEqual('Bobby', timmy.edges[1].vertex.name)

    def test_graph(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        dad = graph.create_vertex('Dad')
        mom = graph.create_vertex('Mom')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, dad, name='parent')
        graph.link_vertices(bobby, mom, name='parent')
        graph.link_vertices(bobby, timmy, name='friend', two_way=True)
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Dad', graph.vertices[1].name)
        self.assertEqual('Mom', graph.vertices[2].name)
        self.assertEqual('Timmy', graph.vertices[3].name)
        self.assertEqual('parent', graph.vertices[0].edges[0].name)
        self.assertEqual('Dad', graph.vertices[0].edges[0].vertex.name)
        self.assertEqual('parent', graph.vertices[0].edges[1].name)
        self.assertEqual('Mom', graph.vertices[0].edges[1].vertex.name)
        self.assertEqual('friend', graph.vertices[0].edges[2].name)
        self.assertEqual('Timmy', graph.vertices[0].edges[2].vertex.name)


class TestEdge(TestCase):
    def test_traverse(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(timmy, bobby.edges[0].traverse())
        self.assertEqual(bobby, timmy.edges[0].traverse())


class TestVertex(TestCase):
    def test_relate(self):
        bobby = Vertex('Bobby')
        timmy = Vertex('Timmy')
        # Register an edge
        edge = Edge(timmy, name='friend', value=2.0)
        bobby.relate(edge)
        # Verify vertices again - but now we have one edge
        self.assertEqual(1, len(bobby.edges))
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual(2.0, bobby.edges[0].value)
        # We didn't actually link these vertices so no edge here
        self.assertEqual(0, len(timmy.edges))
        # Attempt to relate edge twice - This is allowed even though it doesn't make sense
        bobby.relate(edge)
        self.assertEqual(2, len(bobby.edges))
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual('friend', bobby.edges[1].name)
        self.assertEqual(0, len(timmy.edges))
        self.assertEqual('Timmy', bobby.edges[0].vertex.name)
        self.assertEqual('Timmy', bobby.edges[1].vertex.name)

    def test_relate_vertex(self):
        bobby = Vertex('Bobby')
        timmy = Vertex('Timmy')
        bobby.relate_vertex(timmy, 'friend')
        # Verify vertices again - but now we have one edge
        self.assertEqual(1, len(bobby.edges))
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual(1.0, bobby.edges[0].value)
        # We didn't actually link these vertices so no edge here
        self.assertEqual(0, len(timmy.edges))
        # Attempt to relate edge twice - This is allowed even though it doesn't make sense
        bobby.relate_vertex(timmy, 'friend')
        self.assertEqual(2, len(bobby.edges))
        self.assertEqual('friend', bobby.edges[0].name)
        self.assertEqual('friend', bobby.edges[1].name)
        self.assertEqual(0, len(timmy.edges))
        self.assertEqual('Timmy', bobby.edges[0].vertex.name)
        self.assertEqual('Timmy', bobby.edges[1].vertex.name)

