import pytest
from abstract.Graph import Graph  # Assuming you have a Graph class
from abstract.Node import Node  # Assuming you have a Node class


@pytest.fixture
def graph():
    """Fixture to create a graph instance."""
    return Graph()  # Create a graph instance


def test_graph_initialization(graph):
    """Test the initialization of a Graph."""
    assert graph is not None  # Ensure the graph is created


def test_add_node(graph):
    """Test adding a node to the graph."""
    node = Node(graph=graph, name='TestNode')
    graph.add_node(node)  # Assuming this method exists
    assert node in graph.nodes  # Assuming graph has a nodes attribute


def test_remove_node(graph):
    """Test removing a node from the graph."""
    node = Node(graph=graph, name='TestNode')
    # you cannot add a node directly to the graph
    graph.add_node(node)
    graph.remove_node(node)  # Assuming this method exists
    assert node not in graph.nodes

def test_complex_graph():
    """Fixture to create a complex graph."""
    graph = Graph()
    paris = Node(graph=graph, name='Paris')
    france = Node(graph=graph, name='France')
    europe = Node(graph=graph, name='Europe')
    london = Node(graph=graph, name='London')
    england = Node(graph=graph, name='England')
    capital_of_france = paris.connect_to(france)
    france_in_europe = france.connect_to(europe)
    capital_of_england = london.connect_to(england)
    england_in_europe = england.connect_to(europe)

    assert paris.outward_edges_dict == {capital_of_france.id: capital_of_france}
    assert france.outward_edges_dict == {france_in_europe.id: france_in_europe}
    assert london.outward_edges_dict == {capital_of_england.id: capital_of_england}

    assert ('France', 'Europe', None) == france_in_europe.id
    assert france.inward_edges_dict == {capital_of_france.id: capital_of_france}
    assert england.inward_edges_dict == {capital_of_england.id: capital_of_england}

    assert paris.children == [france]
    assert france.children == [europe]
    assert england.children == [europe]
    assert london.children == [england]

    assert paris.parents == []
    assert france.parents == [paris]
    assert europe.parents == [france, england]
    assert england.parents == [london]

    assert paris.ancestors == []
    assert france.ancestors == [paris]
    assert europe.ancestors == [france, paris, england, london]
    assert london.ancestors == []

    assert paris.descendants == [france, europe]
    assert france.descendants == [europe]
    assert europe.descendants == []
    assert london.descendants == [england, europe]

    assert paris.num_descendants == 2
    assert france.num_descendants == 1
    assert europe.num_descendants == 0
    assert london.num_descendants == 2

    # england and france are co-parents because they are both parents of europe
    assert england.co_parents == [france]
    assert france.co_parents == [england]

