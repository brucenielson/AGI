from unittest import TestCase
from graph.graph import Graph, Edge, Vertex


class TestGraph(TestCase):
    def test_create_vertex(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual('Bobby', bobby.name)

    def test_register_vertex(self):
        vertex = Vertex('Bobby')
        graph = Graph()
        graph._register_vertex(vertex)
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual(vertex, graph.get_vertices('Bobby'))
        graph._register_vertex(vertex)
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual(vertex, graph.get_vertices('Bobby'))

    def test_register_edge(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        # Verify vertices and no edges
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(timmy, graph.get_vertices('Timmy'))
        # Register an edge
        edge = Edge(bobby, timmy, name='friend', value=2.0)
        graph._register_edge(bobby, edge)
        # Verify vertices again - but now we have one edge
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(timmy, graph.get_vertices('Timmy'))
        self.assertEqual('friend', bobby.edges_out_list()[0].name)
        self.assertEqual(2.0, bobby.edges_out_list()[0].value)
        # We didn't actually link these vertices so no edge here
        self.assertEqual(0, len(timmy.edges_out))
        # However, we should find it in Timmy's edges_in
        self.assertEqual(edge, timmy.edges_in_list()[0])
        self.assertEqual(1, len(timmy.edges_in))
        # Attempt to register an edge twice
        graph._register_edge(bobby, edge)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(timmy, graph.get_vertices('Timmy'))
        self.assertEqual('friend', bobby.edges_out_list()[0].name)
        self.assertEqual(0, len(timmy.edges_out))
        self.assertEqual(edge, timmy.edges_in_list()[0])
        self.assertEqual(1, len(timmy.edges_in))
        self.assertEqual('Timmy', bobby.edges_out_list()[0].to_vertex.name)

    def test_link_vertices(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        friend_edge = graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        # Verify vertices and no edges
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(2, len(graph.edges))
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(timmy, graph.get_vertices('Timmy'))
        self.assertEqual(1, len(bobby.edges_out))
        self.assertIn(friend_edge, bobby.edges_out_list('friend'))
        self.assertEqual(1.0, friend_edge.value)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual('friend', timmy.edges_out_list('friend')[0].name)
        self.assertEqual('Bobby', timmy.edges_out_list('friend')[0].to_vertex.name)
        self.assertEqual('Timmy', bobby.edges_out_list('friend')[0].to_vertex.name)
        self.assertEqual(1.0, timmy.edges_out_list('friend')[0].value)
        self.assertEqual(1, len(timmy.edges_out_list('friend')))
        self.assertEqual(timmy, bobby.edges_out_list('friend')[0].to_vertex)
        self.assertEqual(bobby, timmy.edges_out_list('friend')[0].to_vertex)
        # Attempt to add a second edge (which is allowed)
        roommate_edge = graph.link_vertices(bobby, timmy, 'roommate', two_way=True)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(4, len(graph.edges))
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(timmy, graph.get_vertices('Timmy'))
        self.assertEqual(2, len(bobby.edges_out))
        self.assertIn(friend_edge, bobby.edges_out_list('friend'))
        self.assertIn(roommate_edge, bobby.edges_out_list('roommate'))
        self.assertEqual(2, len(timmy.edges_out))
        self.assertEqual('friend', timmy.edges_out_list('friend')[0].name)
        self.assertEqual('roommate', timmy.edges_out_list('roommate')[0].name)
        self.assertEqual(2, len(timmy.edges_out))
        self.assertEqual('Timmy', bobby.edges_out_list('friend')[0].to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out_list('friend')[0].to_vertex.name)
        self.assertEqual('Timmy', bobby.edges_out_list('roommate')[0].to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out_list('roommate')[0].to_vertex.name)

    def test_graph(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        dad = graph.create_vertex('Dad')
        mom = graph.create_vertex('Mom')
        timmy = graph.create_vertex('Timmy')
        dad_edge = graph.link_vertices(bobby, dad, name='parent')
        mom_edge = graph.link_vertices(bobby, mom, name='parent')
        friend_edge = graph.link_vertices(bobby, timmy, name='friend', two_way=True)
        self.assertEqual(bobby, graph.get_vertices('Bobby'))
        self.assertEqual(dad, graph.get_vertices('Dad'))
        self.assertEqual(mom, graph.get_vertices('Mom'))
        self.assertEqual(timmy, graph.get_vertices('Timmy'))

        self.assertIn(dad_edge, bobby.edges_out_list('parent'))
        self.assertIn(mom_edge, bobby.edges_out_list('parent'))
        self.assertEqual('Dad', dad_edge.to_vertex.name)
        self.assertEqual('Mom', mom_edge.to_vertex.name)
        self.assertIn(friend_edge, bobby.edges_out_list('friend'))
        self.assertEqual('Timmy', friend_edge.to_vertex.name)

    def test_create_vertex2(self):
        graph = Graph()
        vertex = graph.create_vertex()
        self.assertIn(vertex, graph.vertices)

    def test_link_vertices2(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertIn(edge, vertex_a.edges_out_list())
        self.assertIn(edge, vertex_b.edges_in_list())
        self.assertEqual(edge.from_vertex, vertex_a)
        self.assertEqual(edge.to_vertex, vertex_b)

    def test_link_vertices_two_way(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b, two_way=True)
        edge1 = vertex_a.edges_out_list()[0]
        edge2 = vertex_b.edges_out_list()[0]
        self.assertIn(edge1, vertex_b.edges_in_list())
        self.assertIn(edge2, vertex_a.edges_in_list())

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

    def test_assigning_properties(self):
        v1 = Vertex("A")
        v2 = Vertex("B")
        e = Edge(v1, v2)
        e.name = 'edge'
        e.value = 2
        self.assertEqual('edge', e.name)
        self.assertEqual('A', v1.name)
        self.assertEqual('B', v2.name)
        self.assertEqual(2, e.value)
        v1.name = 'C'
        v2.name = 'D'
        e.name = 'edge 2'
        e.value = 3
        self.assertEqual('edge 2', e.name)
        self.assertEqual('C', v1.name)
        self.assertEqual('D', v2.name)
        self.assertEqual(3, e.value)


class TestEdge(TestCase):
    def test_traverse(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(timmy, bobby.edges_out_list('friend')[0].to_vertex)
        self.assertEqual(bobby, timmy.edges_out_list('friend')[0].to_vertex)


class TestVertex(TestCase):
    def test_edges_out(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual(graph.get_edges()[1], timmy.edges_out_list()[0])
        self.assertEqual(1, len(bobby.edges_out))
        self.assertEqual(graph.get_edges()[0], bobby.edges_out_list()[0])

    def test_edges_in(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(1, len(timmy.edges_in))
        self.assertEqual(graph.get_edges()[0], timmy.edges_in_list()[0])
        self.assertEqual(1, len(bobby.edges_in))
        self.assertEqual(graph.get_edges()[1], bobby.edges_in_list()[0])

    def test_link_vertices_two_way(self):
        graph = Graph(name="TestGraph")
        a = graph.create_vertex(name="A")
        b = graph.create_vertex(name="B")
        e = graph.link_vertices(a, b, name="AB", two_way=True)
        self.assertIsInstance(e, Edge)
        self.assertIn(e, graph.edges)
        self.assertIn(e, a.edges_out)
        self.assertIn(e, b.edges_in)
        self.assertEqual(len(graph.edges), 2)

    def test_edges_list(self):
        graph = Graph(name="TestGraph")
        a = graph.create_vertex(name="A")
        b = graph.create_vertex(name="B")
        graph.link_vertices(a, b, name="AB")
        self.assertEqual(len(graph.get_edges()), 1)
        graph.link_vertices(b, a, name="BA", two_way=True)
        self.assertEqual(len(graph.get_edges()), 3)
        self.assertEqual(len(graph.get_edges(name="AB")), 1)
        self.assertEqual(len(graph.get_edges(name="BA")), 2)
        self.assertEqual(len(graph.get_edges(name="ABC")), 0)

    def test_vertices_list(self):
        graph = Graph()
        vertex1 = graph.create_vertex(name="A")
        vertex2 = graph.create_vertex(name="B")
        vertex3 = graph.create_vertex(name="C")
        vertices = graph.get_vertices()
        self.assertEqual(len(vertices), 3)
        self.assertIn(vertex1, vertices)
        self.assertIn(vertex2, vertices)
        self.assertIn(vertex3, vertices)

    def test_vertices_list_with_name(self):
        graph = Graph()
        vertex1 = graph.create_vertex(name="A")
        vertex2 = graph.create_vertex(name="B")
        vertex3 = graph.create_vertex(name="C")
        vertices = graph.get_vertices()
        self.assertEqual(len(vertices), 3)
        self.assertIn(vertex1, vertices)
        self.assertIn(vertex2, vertices)
        self.assertIn(vertex3, vertices)
