from __future__ import annotations
from typing import Optional, List, Union


class Vertex:
    def __init__(self, name: Optional[str] = None) -> None:
        # Node names are optional for human reading and serve no other purpose
        self.name: str = name
        self._edges_out: List[Edge] = []
        self._edges_in: List[Edge] = []

    @property
    def edges_out(self):
        return self._edges_out

    @property
    def edges_in(self):
        return self._edges_in


class Edge:
    def __init__(self, from_vertex: Vertex, to_vertex: Vertex, name: Optional[str] = None,
                 value: Union[float, int] = 1) -> None:
        # Node names are optional for human reading and serve no other purpose
        self.name: str = name
        self._from_vertex: Vertex = from_vertex
        self._to_vertex: Vertex = to_vertex
        self.value: Union[float, int] = value

    def traverse(self) -> Vertex:
        return self._to_vertex

    @property
    def to_vertex(self):
        return self._to_vertex


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

    def _register_edge(self, from_vertex: Vertex, edge: Edge) -> None:
        if edge not in self.edges and edge not in from_vertex.edges_out and edge not in edge.to_vertex.edges_in:
            self.edges.append(edge)
            from_vertex.edges_out.append(edge)
            edge.to_vertex.edges_in.append(edge)

    # Links vertex_a to vertex_b unless two_way is set to true then it's a two way link
    def link_vertices(self, vertex_a: Vertex, vertex_b: Vertex, name: str = None, two_way: bool = False,
                      value: Union[float, int] = 1) -> None:
        # Add nodes to the list of nodes om the graph
        self._register_vertex(vertex_a)
        self._register_vertex(vertex_b)
        # Create a relationship and save it
        edge1: Edge = Edge(vertex_a, vertex_b, name=name, value=value)
        self._register_edge(vertex_a, edge1)
        if two_way:
            edge2: Edge = Edge(vertex_b, vertex_a, name=name, value=value)
            self._register_edge(vertex_b, edge2)
