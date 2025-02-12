# Abstract 🕸️
Abstract is a Python library designed for creating and visualizing graphs, enabling users to leverage various graph properties effectively.

## Installation

To install the library, simply run:

```bash
pip install abstract
```

## Graph

### Introduction
In computer science, a graph is an abstract data type that implements the concepts of undirected and directed graphs from mathematics, specifically within the field of graph theory. [[1]](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))

A graph data structure consists of a finite (and potentially mutable) set of vertices (or nodes) and a set of unordered pairs of these vertices for undirected graphs, or ordered pairs for directed graphs. These pairs are referred to as edges, arcs, or lines in undirected graphs, and as arrows, directed edges, directed arcs, or directed lines in directed graphs. The vertices may be part of the graph structure or may be represented externally by integer indices or references. [[1]](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))

### Usage
The `Graph` class allows you to create nodes and edges, as well as visualize the resulting graph. Edges can have direction, indicating parent-child relationships.

To create a new graph, use the `Graph()` constructor:

```python
from abstract import Graph

graph = Graph(direction='LR') 
# The default direction is 'LR'; other options include 'TB', 'BT', and 'RL'.
```

### `add_node(...)`
The `add_node` method creates a node in the graph and returns a `Node` object. 

It accepts the following arguments:
* `name`: The name of the new node (should be unique); snake_case is recommended.
* `label` (optional): Any string; if omitted, the name will be displayed.
* `value` (optional): Can be any object.
* `style` (optional): Should be a `NodeStyle` object, used only for rendering.
* `if_node_exists` (optional): Specifies the action if a node with this name already exists; options are 'warn', 'error', or 'ignore'; the default is 'warn'.

To illustrate how the `Graph` class works, let's use the [Rock, Paper, Scissors, Lizard, Spock](https://bigbangtheory.fandom.com/wiki/Rock,_Paper,_Scissors,_Lizard,_Spock) game. The following list shows the order in which an object in the game defeats the object to its right and is defeated by the object to its left. Note that there are only five objects, which are repeated to demonstrate all possible pairs.

```python
node_list = [
    'scissors', 'paper', 'rock', 'lizard', 'Spock', 'scissors',
    'lizard', 'paper', 'Spock', 'rock', 'scissors'
]
```

Now, let's create nodes with the same names:

```python
# Create a set to avoid duplicates
for node in set(node_list):
    graph.add_node(name=node)
    
graph.display(direction='TB')  # The left-right direction is too tall.
```
![image of the graph](http://idin.ca/storage/python/abstract/images/rock_paper_scissors_lizard_spock_1.png)

**Note**: By default, the Graph uses the colour theme from the [colouration](http://pypi.org/project/colouration) library for root nodes and determines the colour of other nodes based on the directionality of edges. In the above example, without any edges, all nodes are considered roots.

### `connect(...)` (Add an Edge)
The `connect` method creates an edge from a `start` node to an `end` node. The `start` and `end` arguments can be either the names of nodes or the `Node` objects themselves.

```python
for i in range(len(node_list) - 1):
    graph.connect(start=node_list[i], end=node_list[i + 1])
graph.display(direction='LR')  # The top-bottom direction is too tall.
```
![image of the graph](http://idin.ca/storage/python/abstract/images/rock_paper_scissors_lizard_spock_2.png)

**Note**: Nodes that form a loop are coloured differently (red circles with yellow interiors).

### *get_node*
To retrieve a node from the graph, use the `get_node` method, which returns a `Node` object.

```python
rock = graph.get_node('rock')
```

### `display(...)`
The `display` method visualizes the graph. If a `path` is provided, it saves the visualization to an image file, which can be in either *pdf* or *png* format. You can also specify the resolution using the `dpi` argument. The file format is inferred from the `path` argument.

```python
# Save as a PNG file and view the file
graph.draw(path='my_graph.png', view=True)
```

### `Graph(obj=...)`
You can create a graph from any object that has a `__graph__()` method. Examples of such objects include: 
* `Graph` class from this library
* `Pensieve` class from the [pensieve](https://pypi.org/project/pensieve/) library
* `Page` class from the [internet.wikipedia](https://pypi.org/project/internet/) submodule

```python
from pensieve import Pensieve
from abstract import Graph

pensieve = Pensieve()
pensieve['two'] = 2
pensieve['three'] = 3
pensieve['four'] = lambda two: two * two
pensieve['five'] = 5
pensieve['six'] = lambda two, three: two * three
pensieve['seven'] = 7
pensieve['eight'] = lambda two, four: two * four
pensieve['nine'] = lambda three: three * three
pensieve['ten'] = lambda two, five: two * five
graph = Graph(obj=pensieve, direction='TB')  # or Graph(pensieve)
graph.display()
```
![image of the graph](http://idin.ca/storage/python/abstract/images/pensieve_numbers_graph.png)

### `random(...)`
The `random` method creates a random graph.

```python
g1 = Graph.random(num_nodes=8, connection_probability=0.4, seed=6)
g1
```
![image of the graph](http://idin.ca/storage/python/abstract/images/random_graph_1.png)

### Adding Two Graphs: `+`
You can easily add two graphs using the `+` operator. The result will contain the union of nodes and edges from both graphs.

```python
g2 = Graph.random(num_nodes=7, start_index=3, connection_probability=0.4, seed=41)
g2
```
![image of the graph](http://idin.ca/storage/python/abstract/images/random_graph_2.png)

```python
g3 = g1 + g2
g3
```
![image of the graph](http://idin.ca/storage/python/abstract/images/random_graph_1_plus_2.png)

### Finding Loops
The `is_in_loop` method of a node helps identify nodes that form a loop; that is, nodes that have at least one descendant that is also an ancestor.

```python
graph_with_loop = Graph()
for letter in 'abcdef':
    graph_with_loop.add_node(letter)
for start, end in [
    ('a', 'b'), ('b', 'c'), ('c', 'a'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'e')
]:
    graph_with_loop.connect(start, end)
graph_with_loop
```
![image of the graph](http://idin.ca/storage/python/abstract/images/graph_with_loop.png)

```python
for node in graph_with_loop.nodes:
    if node.is_in_loop_with(other='a') and node.name != 'a':
        print(node.name, 'is in the same loop as a')
    elif node.is_in_loop():
        print(node.name, 'is in a loop')
    else:
        print(node.name, 'is not in a loop')
```
Output:
```text
a is in a loop
b is in the same loop as a
c is in the same loop as a
d is not in a loop
e is in a loop
f is in a loop
```

## Future Features

* Create a graph from:
  * List of dictionaries
  * DataFrame
* Create a new graph by filtering an existing graph
