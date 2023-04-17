from unittest import TestCase
from graph.graph import Graph, Edge, Vertex, GraphError


class TestGraph(TestCase):
    def test_create_vertex(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual('Bobby', bobby.name)

    def test_register_vertex(self):
        vertex = Vertex('Bobby')
        graph = Graph()
        graph._register_vertex(vertex)
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual(vertex, graph.vertices.filter('Bobby'))
        graph._register_vertex(vertex)
        self.assertEqual(1, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual(vertex, graph.vertices.filter('Bobby'))

    def test_register_edge(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        # Verify vertices and no edges
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(0, len(graph.edges))
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(timmy, graph.vertices.filter('Timmy'))
        # Register an edge
        edge = Edge(bobby, timmy, name='friend', value=2.0)
        graph._register_edge(bobby, edge)
        # Verify vertices again - but now we have one edge
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(timmy, graph.vertices.filter('Timmy'))
        self.assertEqual('friend', bobby.edges_out.index(0).name)
        self.assertEqual(2.0, bobby.edges_out.index(0).value)
        # We didn't actually link these vertices so no edge here
        self.assertEqual(0, len(timmy.edges_out))
        # However, we should find it in Timmy's edges_in
        self.assertEqual(edge, timmy.edges_in.to_list()[0])
        self.assertEqual(1, len(timmy.edges_in))
        # Attempt to register an edge twice
        graph._register_edge(bobby, edge)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(1, len(graph.edges))
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(timmy, graph.vertices.filter('Timmy'))
        self.assertEqual('friend', bobby.edges_out.index(0).name)
        self.assertEqual(0, len(timmy.edges_out))
        self.assertEqual(edge, timmy.edges_in.to_list()[0])
        self.assertEqual(1, len(timmy.edges_in))
        self.assertEqual('Timmy', bobby.edges_out.index(0).to_vertex.name)

    def test_link_vertices(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        friend_edge = graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        # Verify vertices and no edges
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(2, len(graph.edges))
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(timmy, graph.vertices.filter('Timmy'))
        self.assertEqual(1, len(bobby.edges_out))
        self.assertEqual(friend_edge, bobby.edges_out.filter('friend'))
        self.assertEqual(1.0, friend_edge.value)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual('friend', timmy.edges_out.filter('friend').name)
        self.assertEqual('Bobby', timmy.edges_out.filter('friend').to_vertex.name)
        self.assertEqual('Timmy', bobby.edges_out.filter('friend').to_vertex.name)
        self.assertEqual(1.0, timmy.edges_out.filter('friend').value)
        self.assertEqual(bobby, timmy.edges_out.filter('friend').to_vertex)
        self.assertEqual(timmy, bobby.edges_out.filter('friend').to_vertex)
        self.assertEqual(bobby, timmy.edges_out.filter('friend').to_vertex)
        # Attempt to add a second edge (which is allowed)
        roommate_edge = graph.link_vertices(bobby, timmy, 'roommate', two_way=True)
        self.assertEqual(2, len(graph.vertices))
        self.assertEqual(4, len(graph.edges))
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(timmy, graph.vertices.filter('Timmy'))
        self.assertEqual(2, len(bobby.edges_out))
        self.assertEqual(friend_edge, bobby.edges_out.filter('friend'))
        self.assertEqual(roommate_edge, bobby.edges_out.filter('roommate'))
        self.assertEqual(2, len(timmy.edges_out))
        self.assertEqual('friend', timmy.edges_out.filter('friend').name)
        self.assertEqual('roommate', timmy.edges_out.filter('roommate').name)
        self.assertEqual(2, len(timmy.edges_out))
        self.assertEqual('Timmy', bobby.edges_out.filter('friend').to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out.filter('friend').to_vertex.name)
        self.assertEqual('Timmy', bobby.edges_out.filter('roommate').to_vertex.name)
        self.assertEqual('Bobby', timmy.edges_out.filter('roommate').to_vertex.name)

    def test_graph(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        dad = graph.create_vertex('Dad')
        mom = graph.create_vertex('Mom')
        timmy = graph.create_vertex('Timmy')
        dad_edge = graph.link_vertices(bobby, dad, name='parent')
        mom_edge = graph.link_vertices(bobby, mom, name='parent')
        friend_edge = graph.link_vertices(bobby, timmy, name='friend', two_way=True)
        self.assertEqual(bobby, graph.vertices.filter('Bobby'))
        self.assertEqual(dad, graph.vertices.filter('Dad'))
        self.assertEqual(mom, graph.vertices.filter('Mom'))
        self.assertEqual(timmy, graph.vertices.filter('Timmy'))

        self.assertIn(dad_edge, bobby.edges_out.filter('parent', 'name'))
        self.assertIn(mom_edge, bobby.edges_out.filter('parent', 'name'))
        self.assertEqual('Dad', dad_edge.to_vertex.name)
        self.assertEqual('Mom', mom_edge.to_vertex.name)
        self.assertEqual(friend_edge, bobby.edges_out.filter('friend', 'name'))
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
        self.assertIn(edge, vertex_a.edges_out.to_list())
        self.assertIn(edge, vertex_b.edges_in.to_list())
        self.assertEqual(edge.from_vertex, vertex_a)
        self.assertEqual(edge.to_vertex, vertex_b)

    def test_link_vertices_two_way(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b, two_way=True)
        edge1 = vertex_a.edges_out.index(0)
        edge2 = vertex_b.edges_out.index(0)
        self.assertIn(edge1, vertex_b.edges_in.to_list())
        self.assertIn(edge2, vertex_a.edges_in.to_list())

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

    def test_name(self):
        graph = Graph(name='Graph')
        self.assertEqual(graph.name, 'Graph')

    def test_vertices(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        self.assertEqual(graph.vertices.to_list(), [vertex_a, vertex_b])

    def test_edges(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertEqual(graph.edges.to_list(), [edge])

    def test__register_vertex(self):
        graph = Graph()
        vertex = graph.create_vertex()
        self.assertEqual(graph.vertices.to_list(), [vertex])

    def test__register_edge(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertEqual(graph.edges.to_list(), [edge])

    def test_reset_visited(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        vertex_a.visited = True
        vertex_b.visited = True
        graph.reset_visited()
        self.assertFalse(vertex_a.visited)
        self.assertFalse(vertex_b.visited)

    def test_explore(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        vertex_c = graph.create_vertex()
        vertex_d = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b)
        graph.link_vertices(vertex_a, vertex_c)
        graph.link_vertices(vertex_b, vertex_d)
        graph.link_vertices(vertex_c, vertex_d)
        graph.explore(vertex_a.id)
        self.assertTrue(vertex_a.visited)
        self.assertTrue(vertex_b.visited)
        self.assertTrue(vertex_c.visited)
        self.assertTrue(vertex_d.visited)

    def test_explore_graph(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        vertex_c = graph.create_vertex()
        vertex_d = graph.create_vertex()
        vertex_e = graph.create_vertex()
        vertex_f = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b)
        graph.link_vertices(vertex_a, vertex_c)
        graph.link_vertices(vertex_b, vertex_d)
        graph.link_vertices(vertex_c, vertex_d)
        graph.link_vertices(vertex_e, vertex_f)
        graph.explore_graph()
        self.assertTrue(vertex_a.visited)
        self.assertTrue(vertex_b.visited)
        self.assertTrue(vertex_c.visited)
        self.assertTrue(vertex_d.visited)
        self.assertTrue(vertex_e.visited)
        self.assertTrue(vertex_f.visited)

    def test_explore_graph2(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        vertex_c = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b)
        graph.explore_graph()
        self.assertEqual(vertex_a.pre, 0)
        self.assertEqual(vertex_b.pre, 1)
        self.assertEqual(vertex_b.post, 2)
        self.assertEqual(vertex_a.post, 3)
        self.assertEqual(vertex_c.pre, 4)
        self.assertEqual(vertex_a.cc_id, 1)
        self.assertEqual(vertex_b.cc_id, 1)
        self.assertEqual(vertex_c.cc_id, 2)

    def test_is_cyclic(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        vertex_c = graph.create_vertex()
        vertex_d = graph.create_vertex()
        graph.link_vertices(vertex_a, vertex_b)
        graph.link_vertices(vertex_b, vertex_c)
        graph.link_vertices(vertex_c, vertex_d)
        with self.assertRaises(GraphError):
            _ = (lambda: graph.is_cyclic)()
        graph.explore_graph()
        self.assertFalse(graph.is_cyclic)
        graph.link_vertices(vertex_d, vertex_b)
        graph.explore_graph()
        self.assertTrue(graph.is_cyclic)


class TestEdge(TestCase):
    def test_traverse(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(timmy, bobby.edges_out.filter('friend').to_vertex)
        self.assertEqual(bobby, timmy.edges_out.filter('friend').to_vertex)

    def test_is_edge_types_basic(self):
        # Create a graph with 3 vertices and 2 edges forming a directed cycle
        graph = Graph()
        vertex_1 = graph.create_vertex()
        vertex_2 = graph.create_vertex()
        vertex_3 = graph.create_vertex()
        graph.link_vertices(vertex_1, vertex_2)
        graph.link_vertices(vertex_2, vertex_3)
        graph.link_vertices(vertex_3, vertex_1)
        # Explore the graph to set pre- and post-values for all vertices and edges
        graph.explore(vertex_1.id)
        # Test that the two back edges have the correct is_back_edge() value
        back_edges = [edge for edge in graph.edges if edge.is_back_edge]
        self.assertEqual(len(back_edges), 1)
        self.assertTrue(all([edge.is_back_edge for edge in back_edges]))
        # Test that the two forward edges have the correct is_forward_edge() value
        forward_edges = [edge for edge in graph.edges if edge.is_forward_edge]
        self.assertEqual(len(forward_edges), 0)
        self.assertTrue(all([edge.is_forward_edge for edge in forward_edges]))
        # Test that the two cross edges have the correct is_cross_edge() value
        tree_edges = [edge for edge in graph.edges if edge.is_tree_edge]
        self.assertEqual(len(tree_edges), 2)
        self.assertTrue(all([edge.is_tree_edge for edge in tree_edges]))
        # No cross edges should exist
        cross_edges = [edge for edge in graph.edges if edge.is_cross_edge]
        self.assertEqual(len(cross_edges), 0)
        self.assertTrue(all([edge.is_cross_edge for edge in cross_edges]))

    def test_is_edge_types_advance(self):
        # Create a graph with 3 vertices and 2 edges forming a directed cycle
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        vertex_c = graph.create_vertex()
        vertex_d = graph.create_vertex()
        tree1 = graph.link_vertices(vertex_a, vertex_b)
        tree2 = graph.link_vertices(vertex_b, vertex_c)
        tree3 = graph.link_vertices(vertex_b, vertex_d)
        forward = graph.link_vertices(vertex_a, vertex_d)
        cross = graph.link_vertices(vertex_d, vertex_c)
        back = graph.link_vertices(vertex_c, vertex_a)
        # Explore the graph to set pre- and post-values for all vertices and edges
        graph.explore(vertex_a.id)
        # Test everything
        self.assertTrue(tree1.is_tree_edge)
        self.assertFalse(tree1.is_forward_edge)
        self.assertTrue(tree1.is_tree_or_forward_edge)
        self.assertTrue(tree2.is_tree_edge)
        self.assertFalse(tree2.is_forward_edge)
        self.assertTrue(tree3.is_tree_or_forward_edge)
        self.assertTrue(tree3.is_tree_edge)
        self.assertFalse(tree3.is_forward_edge)
        self.assertTrue(tree3.is_tree_or_forward_edge)
        self.assertTrue(forward.is_forward_edge)
        self.assertFalse(forward.is_tree_edge)
        self.assertTrue(forward.is_tree_or_forward_edge)
        self.assertTrue(cross.is_cross_edge)
        self.assertTrue(back.is_back_edge)


class TestVertex(TestCase):
    def test_edges_out(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(1, len(timmy.edges_out))
        self.assertEqual(graph.edges.to_list()[1], timmy.edges_out.index(0))
        self.assertEqual(1, len(bobby.edges_out))
        self.assertEqual(graph.edges.to_list()[0], bobby.edges_out.index(0))

    def test_edges_in(self):
        graph = Graph()
        bobby = graph.create_vertex('Bobby')
        timmy = graph.create_vertex('Timmy')
        graph.link_vertices(bobby, timmy, 'friend', two_way=True)
        self.assertEqual(1, len(timmy.edges_in))
        self.assertEqual(graph.edges.to_list()[0], timmy.edges_in.to_list()[0])
        self.assertEqual(1, len(bobby.edges_in))
        self.assertEqual(graph.edges.to_list()[1], bobby.edges_in.to_list()[0])

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
        ab = graph.link_vertices(a, b, name="AB")
        self.assertEqual(len(graph.edges.to_list()), 1)
        graph.link_vertices(b, a, name="BA", two_way=True)
        self.assertEqual(len(graph.edges.to_list()), 3)
        self.assertEqual(graph.edges.filter("AB"), ab)
        self.assertEqual(len(graph.edges.filter("BA")), 2)
        self.assertEqual(len(graph.edges.filter("ABC")), 0)

    def test_vertices_list(self):
        graph = Graph()
        vertex1 = graph.create_vertex(name="A")
        vertex2 = graph.create_vertex(name="B")
        vertex3 = graph.create_vertex(name="C")
        vertices = graph.vertices
        self.assertEqual(len(vertices), 3)
        self.assertIn(vertex1, vertices)
        self.assertIn(vertex2, vertices)
        self.assertIn(vertex3, vertices)

    def test_vertex_id(self):
        graph = Graph()
        vertex = graph.create_vertex()
        self.assertIsInstance(vertex.id, int)

    def test_edge_id(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertIsInstance(edge.id, int)

    def test_assigning_properties(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        edge.name = 'edge'
        edge.value = 2
        self.assertEqual('edge', edge.name)
        self.assertEqual(2, edge.value)
        vertex_a.name = 'C'
        vertex_b.name = 'D'
        edge.name = 'edge 2'
        edge.value = 3
        self.assertEqual('edge 2', edge.name)
        self.assertEqual('C', vertex_a.name)
        self.assertEqual('D', vertex_b.name)
        self.assertEqual(3, edge.value)

    def test_vertex_properties(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        edge.name = 'edge'
        edge.value = 2
        self.assertEqual('edge', edge.name)
        self.assertEqual(2, edge.value)
        vertex_a.name = 'C'
        vertex_b.name = 'D'
        edge.name = 'edge 2'
        edge.value = 3
        self.assertEqual('edge 2', edge.name)
        self.assertEqual('C', vertex_a.name)
        self.assertEqual('D', vertex_b.name)
        self.assertEqual(3, edge.value)

    def test_edge_properties(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        edge.name = 'edge'
        edge.value = 2
        self.assertEqual('edge', edge.name)
        self.assertEqual(2, edge.value)
        vertex_a.name = 'C'
        vertex_b.name = 'D'
        edge.name = 'edge 2'
        edge.value = 3
        self.assertEqual('edge 2', edge.name)
        self.assertEqual('C', vertex_a.name)
        self.assertEqual('D', vertex_b.name)
        self.assertEqual(3, edge.value)

    # test __str__ and __repr__
    def test_str(self):
        graph = Graph(name='The Graph')
        vertex_a = graph.create_vertex(name="vertex_a")
        vertex_b = graph.create_vertex(name="vertex_b")
        edge = graph.link_vertices(vertex_a, vertex_b, name="edge")
        self.assertEqual(str(edge), 'Edge: edge')
        self.assertEqual(repr(edge), f'Edge({edge.id})')
        self.assertEqual(str(vertex_a), 'Vertex: vertex_a')
        self.assertEqual(repr(vertex_a), f'Vertex({vertex_a.id})')
        self.assertEqual(str(graph), 'The Graph')
        self.assertEqual(repr(graph), 'Graph(The Graph)')

    # Test visited property
    def test_visited(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertFalse(vertex_a.visited)
        self.assertFalse(vertex_b.visited)
        vertex_a.visited = True
        self.assertTrue(vertex_a.visited)
        self.assertFalse(vertex_b.visited)
        vertex_b.visited = True
        self.assertTrue(vertex_a.visited)
        self.assertTrue(vertex_b.visited)
        edge.visited = True
        self.assertTrue(vertex_a.visited)
        self.assertTrue(vertex_b.visited)

    # Test __eq__ and __ne__
    def test_eq(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertEqual(vertex_a, vertex_a)
        self.assertEqual(vertex_b, vertex_b)
        self.assertEqual(edge, edge)
        self.assertNotEqual(vertex_a, vertex_b)
        self.assertNotEqual(vertex_a, edge)
        self.assertNotEqual(vertex_b, edge)
        self.assertNotEqual(vertex_a, None)
        self.assertNotEqual(vertex_b, None)
        self.assertNotEqual(edge, None)
        self.assertNotEqual(vertex_a, 1)
        self.assertNotEqual(vertex_b, 1)
        self.assertNotEqual(edge, 1)
        self.assertNotEqual(vertex_a, 'a')
        self.assertNotEqual(vertex_b, 'a')
        self.assertNotEqual(edge, 'a')
        self.assertNotEqual(vertex_a, [])
        self.assertNotEqual(vertex_b, [])
        self.assertNotEqual(edge, [])

    # Test __hash__
    def test_hash(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertEqual(hash(vertex_a), hash(vertex_a))
        self.assertEqual(hash(vertex_b), hash(vertex_b))
        self.assertEqual(hash(edge), hash(edge))
        self.assertNotEqual(hash(vertex_a), hash(vertex_b))
        self.assertNotEqual(hash(vertex_a), hash(edge))
        self.assertNotEqual(hash(vertex_b), hash(edge))

    def test_name(self):
        graph = Graph()
        vertex_a = graph.create_vertex(name='Vertex 1')
        vertex_b = graph.create_vertex(name='Vertex 2')
        self.assertEqual(vertex_a.name, 'Vertex 1')
        self.assertEqual(vertex_b.name, 'Vertex 2')

    def test_id(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        self.assertGreaterEqual(vertex_a.id, 59)
        self.assertGreaterEqual(vertex_b.id, vertex_a.id)

    def test_from_vertex(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertEqual(edge.from_vertex, vertex_a)

    def test_to_vertex(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b)
        self.assertEqual(edge.to_vertex, vertex_b)

    def test_value(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        vertex_b = graph.create_vertex()
        edge = graph.link_vertices(vertex_a, vertex_b, value=5)
        self.assertEqual(edge.value, 5)

    def test_cc_id(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        self.assertEqual(vertex_a.cc_id, 0)
        vertex_a.cc_id = 1
        self.assertEqual(vertex_a.cc_id, 1)

    def test_pre(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        self.assertEqual(vertex_a.pre, 0)
        vertex_a.pre = 1
        self.assertEqual(vertex_a.pre, 1)

    def test_post(self):
        graph = Graph()
        vertex_a = graph.create_vertex()
        self.assertEqual(vertex_a.post, 0)
        vertex_a.post = 1
        self.assertEqual(vertex_a.post, 1)
