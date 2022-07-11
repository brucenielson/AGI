from __future__ import annotations


class Node:
    def __init__(self, name: str = None):
        # Node names are optional for human reading and serve no other purpose
        self.name = name
        self.node = None
        self.relationships = []

    def relate(self, relationship: Relationship) -> Relationship:
        self.relationships.append(relationship)
        return relationship

    def relate_node(self, node: Node, name: str = None) -> Relationship:
        relationship = Relationship(node, name)
        self.relate(relationship)
        return relationship


class Relationship:
    name: str
    node: Node

    def __init__(self, node: Node, name: str = None):
        # Node names are optional for human reading and serve no other purpose
        self.name = name
        self.node = node

    def traverse(self):
        return self.node


class SemanticNet:
    name: str

    def __init__(self, name: str = None):
        self.name = name
        self.nodes = [Node]
        self.relationships = [Relationship]

    def create_node(self, name: str = None) -> Node:
        # Create a node
        node = Node(name)
        # Save it in the graph
        self.nodes.append(node)
        return node

    def register_node(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)

    def register_relationship(self, relationship: Relationship):
        if relationship not in self.relationships:
            self.relationships.append(relationship)

    # Links node_a to node_b unless two_way is set to true then it's a two way link
    def link_nodes(self, node_a: Node, node_b: Node, name: str = None, two_way: bool = False) -> None:
        # Add nodes to the list of nodes om the graph
        self.register_node(node_a)
        self.register_node(node_b)
        # Create a relationship and save it
        relationship1 = node_a.relate_node(node_b, name)
        self.register_relationship(relationship1)
        if two_way:
            relationship2 = node_b.relate_node(node_a, name)
            self.register_relationship(relationship2)


def main():
    graph = SemanticNet()
    bobby = graph.create_node('Bobby')
    dad = graph.create_node('Dad')
    mom = graph.create_node('Mom')
    timmy = graph.create_node('Timmy')
    graph.link_nodes(bobby, dad, name='parent')
    graph.link_nodes(bobby, mom, name='parent')
    graph.link_nodes(bobby, timmy, name='friend', two_way=True)
    pass


if __name__ == '__main__':
    main()
