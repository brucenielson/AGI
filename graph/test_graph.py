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
        edge = Edge(bobby, timmy, name='friend', value=2.0)
        graph._register_edge(bobby, edge)
        # Verify vertices again - but now we have one edge
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual('friend', bobby.edges_out[0].name)
        self.assertEqual(2.0, bobby.edges_out[0].value)
        # We didn't actually link these vertices so no edge here
        self.assertEqual(0, len(timmy.edges_out))
        # However, we should find it in Timmy's edges_in
        self.assertEqual(edge, timmy.edges_in[0])
        self.assertEqual(1, len(timmy.edges_in))
        # Attempt to register an edge twice
        graph._register_edge(bobby, edge)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual('friend', bobby.edges_out[0].name)
        self.assertEqual(0, len(timmy.edges_out))
        self.assertEqual(edge, timmy.edges_in[0])
        self.assertEqual(1, len(timmy.edges_in))
        self.assertEqual('Timmy', bobby.edges_out[0].to_vertex.name)

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
        self.assertEqual(1, len(bobby.edges_out))
        self.assertEqual('friend', bobby.edges_out[0].name)
        self.assertEqual(1.0, bobby.edges_out[0].value)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual('friend', timmy.edges_out[0].name)
        self.assertEqual(1.0, timmy.edges_out[0].value)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual('Timmy', bobby.edges_out[0].to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out[0].to_vertex.name)
        # Attempt to add a second edge (which is allowed)
        graph.link_vertices(bobby, timmy, 'roommate', two_way=True)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(4, len(graph.edges))
        self.assertEqual('Bobby', graph.vertices[0].name)
        self.assertEqual('Timmy', graph.vertices[1].name)
        self.assertEqual(2, len(bobby.edges_out))
        self.assertEqual('friend', bobby.edges_out[0].name)
        self.assertEqual('roommate', bobby.edges_out[1].name)
        self.assertEqual(2, len(timmy.edges_out))
        self.assertEqual('friend', timmy.edges_out[0].name)
        self.assertEqual('roommate', timmy.edges_out[1].name)
        self.assertEqual(2, len(timmy.edges_out))
        self.assertEqual('Timmy', bobby.edges_out[0].to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out[0].to_vertex.name)
        self.assertEqual('Timmy', bobby.edges_out[1].to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out[1].to_vertex.name)

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
        self.assertEqual('parent', graph.vertices[0].edges_out[0].name)
        self.assertEqual('Dad', graph.vertices[0].edges_out[0].to_vertex.name)
        self.assertEqual('parent', graph.vertices[0].edges_out[1].name)
        self.assertEqual('Mom', graph.vertices[0].edges_out[1].to_vertex.name)
        self.assertEqual('friend', graph.vertices[0].edges_out[2].name)
        self.assertEqual('Timmy', graph.vertices[0].edges_out[2].to_vertex.name)

    def test_create_vertex2(self):
        graph = Graph()
        vertex = graph.create_vertex()
        self.assertIn(vertex, graph.vertices)

    def test_link_vertices2(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertIn(edge, vertex_b.edges_in)
        self.assertEqual(edge.from_vertex, vertex_a)
        self.assertEqual(edge.to_vertex, vertex_b)

    def test_link_vertices_two_way(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b, two_way=True)
        edge1 = vertex_a.edges_out[0]
        edge2 = vertex_b.edges_out[0]
        self.assertIn(edge1, vertex_b.edges_in)
        self.assertIn(edge2, vertex_a.edges_in)
        self.assertEqual(edge1.from_vertex, vertex_a)
        self.assertEqual(edge1.to_vertex, vertex_b)
        self.assertEqual(edge2.from_vertex, vertex_b)
        self.assertEqual(edge2.to_vertex, vertex_a)

    def test_vertex_id(self):
        vertex = Vertex()
        self.assertIsInstance(vertex.id, int)

    def test_edge_id(self):
        vertex_a = Vertex()
        vertex_b = Vertex()
        edge = Edge(vertex_a, vertex_b)
        self.assertIsInstance(edge.id, int)


class TestEdge(TestCase):
    def test_traverse(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(timmy, bobby.edges_out[0].traverse())
        self.assertEqual(bobby, timmy.edges_out[0].traverse())


class TestVertex(TestCase):
    def test_edges_out(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual(graph.edges[1], timmy.edges_out[0])
        self.assertEqual(1, len(bobby.edges_out))
        self.assertEqual(graph.edges[0], bobby.edges_out[0])

    def test_edges_in(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(1, len(timmy.edges_in))
        self.assertEqual(graph.edges[0], timmy.edges_in[0])
        self.assertEqual(1, len(bobby.edges_in))
        self.assertEqual(graph.edges[1], bobby.edges_in[0])
