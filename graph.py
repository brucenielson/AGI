from __future__ import annotations
from typing import Optional, List, Union


class Vertex:
    def __init__(self, name: str = None):
        # Node names are optional for human reading and serve no other purpose
        self.name = name
        self.vertex = None
        self.edges: List[Edge] = []

    def relate(self, edge: Edge) -> None:
        self.edges.append(edge)

    def relate_vertex(self, vertex: Vertex, name: str = None) -> Edge:
        edge = Edge(vertex, name)
        self.relate(edge)
        return edge


class Edge:
    name: str
    vertex: Vertex

    def __init__(self, vertex: Vertex, name: str = None):
        # Node names are optional for human reading and serve no other purpose
        self.name = name
        self.vertex = vertex

    def traverse(self):
        return self.vertex


class Graph:
    name: str

    def __init__(self, name: str = None):
        self.name = name
        self.vertices: List[Vertex] = []
        self.edges: List[Edge] = []

    def create_vertex(self, name: str = None) -> Vertex:
        # Create a vertex
        vertex = Vertex(name)
        # Save it in the graph
        self.vertices.append(vertex)
        return vertex

    def register_vertex(self, vertex: Vertex):
        if vertex not in self.vertices:
            self.vertices.append(vertex)

    def register_edge(self, edge: Edge):
        if edge not in self.edges:
            self.edges.append(edge)

    # Links vertex_a to vertex_b unless two_way is set to true then it's a two way link
    def link_vertices(self, vertex_a: Vertex, vertex_b: Vertex, name: str = None, two_way: bool = False) -> None:
        # Add nodes to the list of nodes om the graph
        self.register_vertex(vertex_a)
        self.register_vertex(vertex_b)
        # Create a relationship and save it
        edge1 = vertex_a.relate_vertex(vertex_b, name)
        self.register_edge(edge1)
        if two_way:
            edge2 = vertex_b.relate_vertex(vertex_a, name)
            self.register_edge(edge2)


def main():
    graph = Graph()
    bobby = graph.create_vertex('Bobby')
    dad = graph.create_vertex('Dad')
    mom = graph.create_vertex('Mom')
    timmy = graph.create_vertex('Timmy')
    graph.link_vertices(bobby, dad, name='parent')
    graph.link_vertices(bobby, mom, name='parent')
    graph.link_vertices(bobby, timmy, name='friend', two_way=True)
    pass


if __name__ == '__main__' or __name__ == 'graph':
    main()
