from __future__ import annotations
from typing import Optional, List, Union
from utils.listdict import IterDict
import uuid
import numpy as np
import copy


def graph_to_adjacency_matrix(graph: Graph) -> np.ndarray:
    """
    Converts a graph to an adjacency matrix.
    :param graph: The graph to convert.
    :return: The adjacency matrix.
    """
    matrix: np.ndarray = np.zeros((len(graph.vertices), len(graph.vertices)))
    i: int
    edge: Edge
    for edge in graph.edges:
        from_vertex: Vertex = edge.from_vertex
        to_vertex: Vertex = edge.to_vertex
        matrix[graph.vertices.index(from_vertex), graph.vertices.index(to_vertex)] = 1
    return matrix


def adjacency_matrix_to_graph(matrix: np.ndarray) -> Graph:
    """
    Converts an adjacency matrix to a graph.
    :param matrix: The adjacency matrix to convert.
    :return: The graph.
    """
    graph: Graph = Graph()
    for i in range(len(matrix)):
        graph.create_vertex()
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i, j] == 1:
                graph.link_vertices(graph.vertices[i], graph.vertices[j])
    return graph


class GraphError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Vertex:
    def __init__(self, name: Optional[str] = None) -> None:
        self._name: Optional[str] = name
        self._edges_out: IterDict[Edge] = IterDict()
        self._edges_in: IterDict[Edge] = IterDict()
        self._visited: bool = False
        self._cc_id: int = 0
        self._pre: int = 0
        self._post: int = 0
        self._id: uuid.UUID = uuid.uuid4()

    def __str__(self) -> str:
        if self._name:
            return f'Vertex: {self._name}'
        else:
            return f'Vertex: {self._id}'

    def __hash__(self) -> int:
        return hash(str(self.id))

    def __repr__(self):
        return f'Vertex({self._id})'

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name

    @property
    def edges_out(self) -> IterDict[Edge]:
        return self._edges_out

    @property
    def edges_in(self) -> IterDict[Edge]:
        return self._edges_in

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def visited(self) -> bool:
        return self._visited

    @visited.setter
    def visited(self, visited: bool) -> None:
        self._visited = visited

    @property
    def cc_id(self) -> int:
        return self._cc_id

    @cc_id.setter
    def cc_id(self, cc_id: int) -> None:
        self._cc_id = cc_id

    @property
    def pre(self) -> int:
        return self._pre

    @pre.setter
    def pre(self, pre: int) -> None:
        self._pre = pre

    @property
    def post(self) -> int:
        return self._post

    @post.setter
    def post(self, post: int) -> None:
        self._post = post


class Edge:
    def __init__(self, from_vertex: Vertex, to_vertex: Vertex, name: Optional[str] = None,
                 value: Union[float, int] = 1) -> None:
        self._name: Optional[str] = name
        self._from_vertex: Vertex = from_vertex
        self._to_vertex: Vertex = to_vertex
        self._value: Union[float, int] = value
        self._id: uuid.UUID = uuid.uuid4()

    def __str__(self) -> str:
        if self.name:
            return f'Edge: {self.name}'
        else:
            return f'Edge: {self._id}'

    def __repr__(self):
        return f'Edge({self._id})'

    def __hash__(self) -> int:
        return hash(str(self.id))

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
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def is_back_edge(self) -> bool:
        return self.to_vertex.pre < self.from_vertex.pre and self.to_vertex.post > self.from_vertex.post

    @property
    def is_tree_or_forward_edge(self) -> bool:
        return self.to_vertex.pre > self.from_vertex.pre and self.to_vertex.post < self.from_vertex.post

    @property
    def is_forward_edge(self) -> bool:
        return self.is_tree_or_forward_edge and not self.is_tree_edge

    @property
    def is_cross_edge(self) -> bool:
        return self.to_vertex.pre < self.from_vertex.pre and self.to_vertex.post < self.from_vertex.pre

    @property
    def is_tree_edge(self) -> bool:
        if self.is_tree_or_forward_edge:
            # A tree edge is a forward edge that has a to_vertex with an edge into it that is not this one
            # that matches the following criteria:
            # 1. This edge is a forward edge
            # 2. There is an edge into the to_vertex that is not this one
            # 3. The other edge's from_vertex into this to_vertex has a higher pre than this edge's from_vertex
            # 4. The other edge's from_vertex into this to_vertex has a lower post than this edge's from_vertex
            for edge in self.to_vertex.edges_in:
                if edge is not self and edge.is_tree_or_forward_edge and \
                        edge.from_vertex.pre > self.from_vertex.pre and edge.from_vertex.post < self.from_vertex.post:
                    return False
            return True
        else:
            return False


class Graph:
    name: str

    def __init__(self, name: Optional[str] = None) -> None:
        self._name = name
        self._vertices: IterDict[Vertex] = IterDict()
        self._edges: IterDict[Edge] = IterDict()
        self._cc_last_id: int = 0
        self._clock: int = 0
        self._explored: bool = False
        self._adjacency_matrix: Optional[np.ndarray] = None

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f'Graph({self._name})'

    @property
    def vertices(self) -> IterDict[Vertex]:
        return self._vertices

    @property
    def edges(self) -> IterDict[Edge]:
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
        self._explored = False
        self._cc_last_id = 0
        for vertex in self.vertices:
            vertex.visited = False

    def _pre_visit(self, vertex: Vertex) -> None:
        vertex.visited = True
        vertex.cc_id = self._cc_last_id
        vertex.pre = self._clock
        self._clock += 1

    def _post_visit(self, vertex: Vertex) -> None:
        vertex.post = self._clock
        self._clock += 1

    # explore a graph using depth first search
    def explore(self, vertex: Union[uuid.UUID, Vertex]) -> List[Vertex]:
        if isinstance(vertex, uuid.UUID):
            vertex_id = vertex
        else:
            vertex_id = vertex.id
        self._pre_visit(self._vertices[vertex_id])
        for edge in self.vertices[vertex_id].edges_out:
            if not edge.to_vertex.visited:
                self.explore(edge.to_vertex.id)
        self._post_visit(self.vertices[vertex_id])
        return self.vertices.to_list()

    # Depth first search using explore to explore the whole graph
    def explore_graph(self) -> None:
        self.reset_visited()
        # Get a list of vertices ids
        vertices: IterDict[Vertex] = self.vertices
        # Explore the graph
        for vertex in vertices:
            if not self._vertices[vertex.id].visited:
                self._cc_last_id += 1
                self.explore(vertex.id)
        # Mark the graph as explored
        self._explored = True

    def is_cyclic(self, allow_explore=True) -> bool:
        # If the graph has not been explored yet, explore it
        if allow_explore and not self._explored:
            self.explore_graph()
        # Throw an error if the graph has not been explored yet
        if not self._explored:
            raise GraphError('Graph has not been explored yet so we cannot determine if it is cyclic or not.')
        for edge in self.edges:
            if edge.is_back_edge:
                return True
        return False

    def is_dag(self, allow_explore=True) -> bool:
        return not self.is_cyclic(allow_explore=allow_explore)

    def is_tree(self, allow_explore=True) -> bool:
        # If the graph has not been explored yet, explore it
        if allow_explore and not self._explored:
            self.explore_graph()
        # Throw an error if the graph has not been explored yet
        if not self._explored:
            raise GraphError('Graph has not been explored yet so we cannot determine if it is a tree or not.')
        for edge in self.edges:
            if not edge.is_tree_edge:
                return False
        return True

    def is_connected(self, vertex_a: Union[Vertex, uuid.UUID, str, int],
                     vertex_b: Union[Vertex, uuid.UUID, str, int]) -> bool:
        # Check to see if vertex_a is directly connected to vertex_b by an edge
        if isinstance(vertex_a, (uuid.UUID, (str, int))):
            vertex_a = self.vertices[vertex_a]
        if isinstance(vertex_b, (uuid.UUID, (str, int))):
            vertex_b = self.vertices[vertex_b]
        for edge in vertex_a.edges_out:
            if edge.to_vertex == vertex_b:
                return True
        return False

    def _update_adjacency_matrix(self) -> None:
        self._adjacency_matrix = graph_to_adjacency_matrix(self)

    # Get a list of linearized vertices
    def linearize(self, allow_explore: bool = True) -> List[Vertex]:
        # If the graph has not been explored yet, explore it
        if allow_explore and not self._explored:
            self.explore_graph()
        # Throw an error if the graph has not been explored yet
        if not self._explored:
            raise GraphError('Graph has not been explored yet so we cannot linearize it.')
        # Verify this is a dag or throw an error
        if not self.is_dag(allow_explore=False):
            raise GraphError('Graph is not a DAG so we cannot linearize it.')
        # Get a list of vertices ids
        vertices: IterDict[Vertex] = self.vertices
        # Sort the vertices by post order
        vertices.sort(key=lambda x: x.post)
        return vertices.to_list()
