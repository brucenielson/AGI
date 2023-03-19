from __future__ import annotations
from typing import Optional, List, Union, Dict, TypeVar, Any


class GraphError(Exception):
    def __init__(self, message):
        super().__init__(message)


T = TypeVar('T')


class ListDict:
    def __init__(self):
        self._values: List[T] = []
        self._id_map: Dict[int, int] = {}

    def __getitem__(self, key: int) -> T:
        index = self._id_map[key]
        return self._values[index]

    def __setitem__(self, key: int, value: T) -> None:
        if key in self._id_map:
            index = self._id_map[key]
            self._values[index] = value
        else:
            self._id_map[key] = len(self._values)
            self._values.append(value)

    def __delitem__(self, key: int) -> None:
        index = self._id_map[key]
        del self._id_map[key]
        del self._values[index]

    def __contains__(self, key: int) -> bool:
        return key in self._values

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def values(self) -> List[T]:
        return self._values

    def filter(self, value: Any, attr_name: str = 'name', ) -> Union[List[T], T]:
        result: List[T] = []
        for item in self._values:
            if hasattr(item, attr_name) and getattr(item, attr_name) == value:
                result.append(item)
            elif isinstance(item, dict) and attr_name in item and item[attr_name] == value:
                result.append(item)
        return result

    def to_list(self):
        result: List[T] = []
        for item in self._values:
            result.append(item)
        return result

    def index(self, index: int) -> T:
        return self._values[index]


class Vertex:
    _id: int = 0

    def __init__(self, name: Optional[str] = None) -> None:
        self._name: Optional[str] = name
        self._edges_out: ListDict[Edge] = ListDict()
        self._edges_in: ListDict[Edge] = ListDict()
        self._id = Vertex._id
        Vertex._id += 1

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name

    @property
    def edges_out(self) -> ListDict[Edge]:
        return self._edges_out

    @property
    def edges_in(self) -> ListDict[Edge]:
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
        self.vertices: ListDict[Vertex] = ListDict()
        self.edges: ListDict[Edge] = ListDict()

    def create_vertex(self, name: Optional[str] = None) -> Vertex:
        # Create a vertex
        vertex = Vertex(name)
        # Save it in the graph
        self.vertices[vertex.id] = vertex
        return vertex

    def _register_vertex(self, vertex: Vertex) -> None:
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex

    def _register_edge(self, from_vertex: Vertex, edge: Edge) -> None:
        if edge.id not in self.edges and edge not in from_vertex.edges_out and edge not in edge.to_vertex.edges_in:
            self.edges[edge.id] = edge
            from_vertex.edges_out[edge.id] = edge
            edge.to_vertex.edges_in[edge.id] = edge

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
        return edge1
