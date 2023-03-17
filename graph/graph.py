from __future__ import annotations
from typing import Optional, List, Union
import uuid


class Vertex:
    _id: int = 0

    def __init__(self, name: Optional[str] = None) -> None:
        self._name: Optional[str] = name
        self._edges_out: List[Edge] = []
        self._edges_in: List[Edge] = []
        self._id = Vertex._id
        Vertex._id += 1

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name

    @property
    def edges_out(self) -> List[Edge]:
        return self._edges_out

    @property
    def edges_in(self) -> List[Edge]:
        return self._edges_in

    @property
    def id(self) -> int:
        return self._id


class Edge:
    _id: int = 0

    def __init__(self, from_vertex: Vertex, to_vertex: Vertex, name: Optional[str] = None,
                 value: Union[float, int] = 1) -> None:
        self._name: Optional[str] = name
        self._from_vertex: Vertex = from_vertex
        self._to_vertex: Vertex = to_vertex
        self._value: Union[float, int] = value
        self._id = Edge._id
        Edge._id += 1

    def traverse(self) -> Vertex:
        return self._to_vertex

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name

    @property
    def from_vertex(self) -> Vertex:
        return self._from_vertex

    @property
    def to_vertex(self) -> Vertex:
        return self._to_vertex

    @property
    def value(self) -> Union[float, int]:
        return self._value

    @value.setter
    def value(self, value: Union[float, int]) -> None:
        self._value = value

    @property
    def id(self) -> int:
        return self._id


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

    def link_vertices(self, vertex_a: Vertex, vertex_b: Vertex, name: Optional[str] = None, two_way: bool = False,
                      value: Union[float, int] = 1) -> Edge:
        # Add nodes to the list of nodes in the graph
        self._register_vertex(vertex_a)
        self._register_vertex(vertex_b)
        # Create a relationship and save it
        edge1: Edge = Edge(vertex_a, vertex_b, name=name, value=value)
        self._register_edge(vertex_a, edge1)
        if two_way:
            edge2: Edge = Edge(vertex_b, vertex_a, name=name, value=value)
            self._register_edge(vertex_b, edge2)
            return edge2
        return edge1
