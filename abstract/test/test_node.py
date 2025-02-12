import pytest
from abstract.Edge import Edge
from abstract.Node import Node
from abstract.Graph import Graph  # Assuming you have a Graph class
from abstract.styling.NodeStyle import NodeStyle  # Assuming you have a NodeStyle class

def test_node_initialization():
    """Test the initialization of a Node."""
    graph = Graph()  # Create a graph instance
    node = Node(graph=graph, name='TestNode', value=42, label='Test Node')
    child_node = Node(graph=graph, name='ChildNode', value=42, label='Child Node')
    edge = Edge(graph=graph, start=node, end=child_node, id='edge1')
    assert node.name == 'TestNode'
    assert node.value == 42
    assert node.label == 'Test Node'
    assert isinstance(node.style, NodeStyle) or node.style is None  # Assuming default style is NodeStyle


def test_node_style():
    """Test setting and getting the style of a Node."""
    style = NodeStyle()  # Create a NodeStyle instance
    graph = Graph()  # Create a graph instance
    node = Node(graph=graph, name='TestNode', value=42, label='Test Node')
    child_node = Node(graph=graph, name='ChildNode', value=42, label='Child Node')
    edge = Edge(graph=graph, start=node, end=child_node, id='edge1')
    node.style = style
    assert node.style == style


def test_add_child():
    """Test adding a child node."""
    graph = Graph()  # Create a graph instance
    node = Node(graph=graph, name='TestNode', value=42, label='Test Node')
    child_node = Node(graph=graph, name='ChildNode', value=42, label='Child Node')
    node.append_outward_edge(child_node)  # Assuming this method exists
    assert child_node in node.outward_edges_dict.values()
