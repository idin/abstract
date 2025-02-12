import pytest
from abstract.Edge import Edge
from abstract.Graph import Graph  # Assuming you have a Graph class
from abstract.Node import Node  # Assuming you have a Node class
from abstract.styling.EdgeStyle import EdgeStyle  # Assuming you have an EdgeStyle class


@pytest.fixture
def graph():
    """Fixture to create a graph instance."""
    return Graph()  # Create a graph instance


@pytest.fixture
def start_node(graph):
    """Fixture to create a start node."""
    return Node(graph=graph, name='StartNode')


@pytest.fixture
def end_node(graph):
    """Fixture to create an end node."""
    return Node(graph=graph, name='EndNode')


@pytest.fixture
def edge(start_node, end_node):
    """Fixture to create an edge instance."""
    return Edge(graph=start_node.graph, start=start_node, end=end_node, id='edge1')


def test_edge_initialization(edge):
    """Test the initialization of an Edge."""
    assert edge.start == edge.start
    assert edge.end == edge.end
    assert edge.raw_id == 'edge1'


def test_edge_style(edge):
    """Test setting and getting the style of an Edge."""
    style = EdgeStyle()  # Create an EdgeStyle instance
    edge.style = style
    assert edge.style == style


def test_remove_edge(edge):
    """Test removing the edge from its nodes."""
    start_node = edge.start
    end_node = edge.end
    edge.remove_self()
    assert edge._start is None
    assert edge._end is None
    assert edge.graph is None
    assert start_node.outward_edges_dict == {}
    assert end_node.inward_edges_dict == {}

