# *Abstract*
Abstract is a Python library for creating and drawing graphs 
and taking advantage of graph properties.

## Installation

```bash
pip install abstract
```
or
```bash
pip install git+https://github.com/idin/abstract.git
```

## *Graph*

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
The *Graph* class allows you to create nodes and edges and 
visualize the resulting graph. Edges can have direction which
indicates parent-child relationship.

To construct a new graph, use *Graph()*.
```python
from abstract import Graph

graph = Graph()
```

### *add_node*
The *add_node* method creates a node in the graph 
and returns a *Node* object. 

It takes the following arguments:
* *name*: name of the new node (should be unique); snake case is recommended
* *label* (optional): it can be any string, if it is missing the name will be displayed
* *value* (optional): can be any object
* *style* (optional): it should be a *NodeStyle* object and is only used for rendering
* *if_node_exists*: what to do if a node with this name exists 
and can be 'warn', 'error', or 'ignore'; default is 'warn'


```python
node_order = [
    'scissors', 'paper', 'rock', 'lizard', 'Spock', 'scissors',
    'lizard', 'paper', 'Spock', 'rock', 'scissors'
]

# add nodes (avoid duplicates)
for node in set(node_order):
    node = graph.add_node(name=node)
```

### *connect* (add an edge)
The *connect* method creates an edge from a *start* node to an *end* node. 
The *start* and *end* arguments can be either names of nodes or the *Node* objects.

```python
for index in range(len(node_order)-1):
    edge = graph.connect(start=node_order[index], end=node_order[index+1])
```

### *get_node*
To retrieve a node from the graph you can use the *get_node* method 
which returns a *Node* object.
```python
rock = graph.get_node('rock')
```

### *draw* (*render*)
The *render* method visualizes the graph and if a *path* is provided it saves it
to an image file that can be a *pdf* or *png*. The file format is infered from 
the *path* argument. The *draw* method is just an alias for *render*.

```python
# just visualize the graph
graph.draw()
```
![image of the graph](https://raw.githubusercontent.com/idin/abstract/master/pictures/rock_paper.png)


```python
# save as a png file and view the file
graph.draw(path='my_graph.png', view=True)

```

### *Graph(obj)*
You can create a graph from any object that has a "*\_\_graph\_\_()*" method. 
Examples of such objects are: 
* *Graph* class from this library
* *Pensieve* class from the [pensieve](https://pypi.org/project/pensieve/) library

```python
from pensieve import Pensieve
from abstract import Graph

pensieve = Pensieve()
pensieve['one'] = 1
pensieve['two'] = 2
pensieve.store(key='three', precursors=['one', 'two'], function=lambda x: x['one'] + x['two'])
graph = Graph(pensieve)
```

### *draw_graph*
In case you just want to draw the graph of an object or create a graph and immediately render it
you can just use the *draw_graph* method. It accepts anything that the *Graph* class accepts.

```python
from pensieve import Pensieve
from abstract import draw_graph

pensieve = Pensieve()
pensieve['one'] = 1
pensieve['two'] = 2
pensieve.store(key='three', precursors=['one', 'two'], function=lambda x: x['one'] + x['two'])
draw_graph(pensieve)
```


## Future Features

* Create a graph from:
  * list of dictionaries
  * dataframe
* Create a new graph by filtering a graph
