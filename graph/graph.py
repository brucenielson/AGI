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

    def __contains__(self, key: T) -> bool:
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
        if index < 0 or index >= len(self._values):
            raise GraphError(f'Index {index} out of range')
        return self._values[index]


class Vertex:
    _id: int = 0

    def __init__(self, name: Optional[str] = None) -> None:
        self._name: Optional[str] = name
        self._edges_out: ListDict[Edge] = ListDict()
        self._edges_in: ListDict[Edge] = ListDict()
        self._id = Vertex._id
        self._visited: bool = False
        Vertex._id += 1

    def __str__(self) -> str:
        if self._name:
            return f'Vertex: {self._name}'
        else:
            return f'Vertex: {self._id}'

    def __hash__(self) -> int:
        return self.id

    def __repr__(self):
        return f'Vertex({self._id})'

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

    @property
    def visited(self) -> bool:
        return self._visited

    @visited.setter
    def visited(self, visited: bool) -> None:
        self._visited = visited

    def pre_visit(self) -> None:
        self.visited = True

    def post_visit(self) -> None:
        pass


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

    def __str__(self) -> str:
        if self.name:
            return f'Edge: {self.name}'
        else:
            return f'Edge: {self._id}'

    def __repr__(self):
        return f'Edge({self._id})'

    def __hash__(self) -> int:
        return self.id

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
        self._name = name
        self._vertices: ListDict[Vertex] = ListDict()
        self._edges: ListDict[Edge] = ListDict()

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f'Graph({self._name})'

    @property
    def vertices(self) -> ListDict[Vertex]:
        return self._vertices

    @property
    def edges(self) -> ListDict[Edge]:
        return self._edges

    @property
    def name(self) -> Optional[str]:
        return self._name

    def create_vertex(self, name: Optional[str] = None) -> Vertex:
        # Create a vertex
        vertex = Vertex(name)
        # Save it in the graph
        self.vertices[vertex.id] = vertex
        return vertex

    def _register_vertex(self, vertex: Vertex) -> None:
        if vertex not in self.vertices:
            self.vertices[vertex.id] = vertex

    def _register_edge(self, from_vertex: Vertex, edge: Edge) -> None:
        if edge not in self.edges and edge not in from_vertex.edges_out \
                and edge not in edge.to_vertex.edges_in:
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

    # Reset all visited flags for Vertices
    def reset_visited(self) -> None:
        for vertex in self.vertices.values():
            vertex.visited = False

    # explore a graph
    def explore(self, vertex_id: int) -> List[Vertex]:
        self._vertices[vertex_id].pre_visit()
        for edge in self._vertices[vertex_id].edges_out:
            if not edge.to_vertex.visited:
                self.explore(edge.to_vertex.id)
        self._vertices[vertex_id].post_visit()
        return self.vertices.to_list()

    # Depth first search using explore to explore the whole graph
    def dfs(self) -> None:
        self.reset_visited()
        # Get a list of vertices ids
        vertices: List[Vertex] = self.vertices.values()
        # Explore the graph
        for vertex in vertices:
            if not self._vertices[vertex.id].visited:
                self.explore(vertex.id)
