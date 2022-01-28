# *Abstract*
Abstract is a Python library for creating and drawing graphs 
and taking advantage of graph properties.

## Installation

```bash
pip install abstract
```

## Graph

### Introduction
In computer science, a graph is an abstract data type that 
is meant to implement the undirected graph and directed graph 
concepts from mathematics; specifically, the field of graph theory. 
[[1]](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))

A graph data structure consists of a finite (and possibly mutable) 
set of vertices or nodes or points, together with a set of 
unordered pairs of these vertices for an undirected graph or 
a set of ordered pairs for a directed graph. These pairs are known 
as edges, arcs, or lines for an undirected graph and as arrows, 
directed edges, directed arcs, or directed lines for a directed graph. 
The vertices may be part of the graph structure, or may be external 
entities represented by integer indices or references. 
[[1]](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))



### Usage
The `Graph` class allows you to create nodes and edges and 
visualize the resulting graph. Edges can have direction which
indicates parent-child relationship.

To construct a new graph, use *Graph()*.
```python
from abstract import Graph

graph = Graph(direction='LR') 
# default direction is 'LR', other options are: 'TB', 'BT', 'RL'
```

### `add_node(...)`
The `add_node` method creates a node in the graph 
and returns a *Node* object. 

It takes the following arguments:
* `name`: name of the new node (should be unique); snake case is recommended
* `label` (optional): it can be any string, if it is missing the name will be displayed
* `value` (optional): can be any object
* `style` (optional): it should be a *NodeStyle* object and is only used for rendering
* `if_node_exists` (optional): what to do if a node with this name exists 
and can be 'warn', 'error', or 'ignore'; default is 'warn'

Let's use the 
[Rock, Paper, Scissors, Lizard, Spock](https://bigbangtheory.fandom.com/wiki/Rock,_Paper,_Scissors,_Lizard,_Spock) 
game to show how `Graph` works. The following list shows the order in which
an object in the game beats the object to its right of it in the list and 
gets beaten by the object left of it. Please note that there are only five
objects and they are repeated to illustrate all possible pairs.

```python
node_list = [
    'scissors', 'paper', 'rock', 'lizard', 'Spock', 'scissors',
    'lizard', 'paper', 'Spock', 'rock', 'scissors'
]
```

Now let's create `nodes` with the same names:
```python
# create a set to avoid duplicates
for node in set(node_list):
    node = graph.add_node(name=node)
    
graph.display(direction='TB') # left-right direction is too tall
```
![image of the graph](http://idin.ca/storage/python/abstract/images/rock_paper_scissors_lizard_spock_1.png)

**Note**: by default, Graph uses colour theme from the 
[colouration](http://pypi.org/project/colouration) library for roots and uses
the directionality of edges to determine the colour of other nodes.
In the above example, without any edges, all nodes are roots.

### `connect(...)` (add an edge)
The `connect` method creates an `edge` from a `start` node to an `end` node. 
The `start` and `end` arguments can be either names of nodes or the `Node` objects.

```python
for i in range(len(node_list)-1):
    edge = graph.connect(start=node_list[i], end=node_list[i + 1])
graph.display(direction='LR') # top-bottom direction is too tall
```
![image of the graph](http://idin.ca/storage/python/abstract/images/rock_paper_scissors_lizard_spock_2.png)

**Note**: nodes that form a loop are coloured differently 
(red circles with yellow colour inside)

### *get_node*
To retrieve a node from the graph you can use the *get_node* method 
which returns a *Node* object.
```python
rock = graph.get_node('rock')
```

### `display(...)`
The `display` method visualizes the graph and if a `path` is provided it saves it
to an image file that can be a *pdf* or *png*; 
you can also provide the resolution with the `dpi` argument. 
The file format is infered from 
the `path` argument. 

```python
# save as a png file and view the file
graph.draw(path='my_graph.png', view=True)

```

### `Graph(obj=...)`
You can create a graph from any object that has a `__graph__()` method. 
Examples of such objects are: 
* `Graph` class from this library
* `Pensieve` class from the [pensieve](https://pypi.org/project/pensieve/) library
* `Page` class from [internet.wikipedia](https://pypi.org/project/internet/) submodule

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
graph = Graph(obj=pensieve, direction='TB') # or Graph(pensieve)
graph.display()
```
![image of the graph](http://idin.ca/storage/python/abstract/images/pensieve_numbers_graph.png)


### `random(...)`
The `random` method creates a random Graph.

```python
g1 = Graph.random(num_nodes=8, connection_probability=0.4, seed=6)
g1
```
![image of the graph](http://idin.ca/storage/python/abstract/images/random_graph_1.png)

### Adding Two Graphs: `+`
You can easily add two graphs using the `+` operator. 
The result will have the union of nodes and edges in both graphs.

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
The `node`'s `is_in_loop` method helps you find nodes that form a loop;
*i.e.*, nodes that have at least one descendant which is also an ancestor.

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
output:
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
  * list of dictionaries
  * dataframe
* Create a new graph by filtering a graph
