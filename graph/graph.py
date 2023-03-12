from __future__ import annotations
from typing import Optional, List


class Vertex:
    def __init__(self, name: Optional[str] = None) -> None:
        # Node names are optional for human reading and serve no other purpose
        self.name = name
        self.edges: List[Edge] = []

    def relate(self, edge: Edge) -> None:
        self.edges.append(edge)

    def relate_vertex(self, vertex: Vertex, name: Optional[str] = None, value: float = 1.0) -> Edge:
        edge = Edge(vertex, name=name, value=value)
        self.relate(edge)
        return edge


class Edge:
    name: str
    vertex: Vertex

    def __init__(self, vertex: Vertex, name: Optional[str] = None, value: float = 1.0) -> None:
        # Node names are optional for human reading and serve no other purpose
        self.name = name
        self.vertex = vertex
        self.value = value

    def traverse(self) -> Vertex:
        return self.vertex


class Graph:
    name: str

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self.vertices: List[Vertex] = []
        self.edges: List[Edge] = []

    def create_vertex(self, name: Optional[str] = None) -> Vertex:
        # Create a vertex
        vertex = Vertex(name)
        # Save it in the graph
        self.vertices.append(vertex)
        return vertex

    def _register_vertex(self, vertex: Vertex) -> None:
        if vertex not in self.vertices:
            self.vertices.append(vertex)

    def _register_edge(self, edge: Edge) -> None:
        if edge not in self.edges:
            self.edges.append(edge)

    # Links vertex_a to vertex_b unless two_way is set to true then it's a two way link
    def link_vertices(self, vertex_a: Vertex, vertex_b: Vertex, name: str = None, two_way: bool = False,
                      value: float = 1.0) -> None:
        # Add nodes to the list of nodes om the graph
        self._register_vertex(vertex_a)
        self._register_vertex(vertex_b)
        # Create a relationship and save it
        edge1 = vertex_a.relate_vertex(vertex_b, name=name, value=value)
        self._register_edge(edge1)
        if two_way:
            edge2 = vertex_b.relate_vertex(vertex_a, name=name, value=value)
            self._register_edge(edge2)
