from .Node import Node
from .Edge import Edge
from .styling.EdgeStyle import EdgeStyle
from .styling.NodeStyle import NodeStyle
from .get_ancestors import get_ancestors
from .get_descendants import get_descendants
from .parse_indentations_function import parse_indentations

import warnings
from copy import deepcopy
from typing import Optional, List, Union, Dict, Tuple


class BasicGraph:
	def __init__(self, strict: bool = True, ordering: bool = True, node_label_converter: Optional[callable] = None, edge_label_converter: Optional[callable] = None):
		"""
		Initializes a BasicGraph instance.

		Args:
			strict (bool): If True, the graph will be strict.
			ordering (bool): If True, the graph will maintain ordering.
			node_label_converter (Optional[callable]): Function to convert node labels.
			edge_label_converter (Optional[callable]): Function to convert edge labels.
		"""
		self._nodes_dict = {}
		self._is_strict = strict
		self._ordering = ordering
		self._nodes_have_graph = True
		self._node_counter = 0
		self._node_label_converter = node_label_converter
		self._edge_label_converter = edge_label_converter
		# if a dictionary or an object with a __graph__() method is passed use that to create the graph

	_STATE_ATTRIBUTES = ['_nodes_dict', '_is_strict', '_ordering', '_node_counter']

	#  for pickling and copying
	def __getstate__(self) -> Dict:
		"""Returns the state of the graph for pickling."""
		state = {
			attr: getattr(self, attr)
			for attr in self._STATE_ATTRIBUTES
		}
		state['_nodes_have_graph'] = False
		return state

	#  for pickling and copying
	def __setstate__(self, state: Dict):
		"""Restores the state of the graph from a pickled state."""
		for key, value in state.items():
			setattr(self, key, value)
		if not self._nodes_have_graph:
			for node in self.nodes:
				node._graph = self

	# methods that return a new graph
	def copy(self) -> 'BasicGraph':
		"""Creates a copy of the graph.

		Returns:
			BasicGraph: A copy of the graph.
		"""
		return deepcopy(self)

	def filter(self, nodes: Optional[List[Union[str, Node]]] = None, direction: str = 'to_and_from', filter_type: str = 'include') -> 'BasicGraph':
		"""
		Filters nodes out or in and returns a new graph.

		Args:
			nodes (Optional[List[Union[str, Node]]]): Nodes to filter.
			direction (str): Direction of filtering.
			filter_type (str): 'include' means only these nodes, 'exclude' means all nodes but these nodes.

		Returns:
			BasicGraph: The filtered graph.
		"""
		nodes = nodes or []
		relatives = {}
		for x in nodes:
			node = self.get_node(node=x)
			name = node.name
			relatives[name] = 1
			if direction == 'to' or 'to_and_from':
				for ancestor in node.ancestors:
					relatives[ancestor.name] = 1

			if direction == 'from' or 'to_and_from':
				for descendant in node.descendants:
					relatives[descendant.name] = 1

		if filter_type == 'include':
			to_delete = [name for name in self.nodes_dict.keys() if name not in relatives]
		else:
			to_delete = relatives.keys()

		new_graph = self.copy()
		for name in to_delete:
			new_graph.remove_node(node=name)
		return new_graph

	@classmethod
	def from_lists(cls, start: List[str], end: List[str], edge: List[Optional[str]], strict: bool = False) -> 'BasicGraph':
		"""
		Creates a graph from lists of start and end nodes.

		Args:
			start (List[str]): List of start nodes.
			end (List[str]): List of end nodes.
			edge (List[Optional[str]]): List of edges.
			strict (bool): If True, the graph will be strict.

		Returns:
			BasicGraph: The created graph.
		"""
		graph = cls(strict=strict)
		for index, start_name, end_name, edge_name in zip(range(len(start)), start, end, edge):
			start_node = graph.add_node(name=start_name, if_node_exists='ignore')
			end_node = graph.add_node(name=end_name, if_node_exists='ignore')
			graph.connect(start=start_node, end=end_node, id=index, label=edge_name)
		return graph

	@classmethod
	def from_object(cls, obj, strict: bool = False, max_depth: Optional[int] = None, max_height: Optional[int] = None) -> 'BasicGraph':
		"""
		Creates a graph from an object with __children__() and __parents__() methods.

		Args:
			obj: The object to create the graph from.
			strict (bool): If True, the graph will be strict.
			max_depth (Optional[int]): Maximum depth for traveling through objects' children.
			max_height (Optional[int]): Maximum height for traveling through objects' parents.

		Returns:
			BasicGraph: The created graph.
		"""
		graph = cls(strict=strict)
		graph.add_node(name=obj.__hash__(), label=str(obj))
		descendants = get_descendants(obj=obj, distance=False, max_depth=max_depth)
		ancestors = get_ancestors(obj=obj, distance=False, max_height=max_height)

		obj_and_descendants = [obj] + descendants
		for child in descendants:
			for parent in child.__parents__():
				if parent in obj_and_descendants:
					graph.add_node(name=child.__hash__(), label=str(child))
					graph.connect(start=parent.__hash__(), end=child.__hash__())

		obj_and_ancestors = [obj] + ancestors
		for parent in ancestors:
			for child in parent.__children__():
				if child in obj_and_ancestors:
					graph.add_node(name=parent.__hash__(), label=str(parent))
					graph.connect(start=parent.__hash__(), end=child.__hash__())

		return graph

	@classmethod
	def from_indented_text(cls, root: str, lines: List[str], indent: Optional[str] = None) -> 'BasicGraph':
		"""
		Converts indented text into a graph.

		Args:
			root (str): The root node.
			lines (List[str]): The lines of text.
			indent (Optional[str]): Used for parsing depth.

		Returns:
			BasicGraph: The created graph.
		"""
		graph = cls(strict=True)
		graph.add_node(name='root', label=root)
		lines = parse_indentations(lines, indent=indent)

		for index, level, content, parent_index in lines:
			graph.add_node(name=str(index), label=f'line {index}')

			if parent_index is not None:
				graph.connect(start=str(parent_index), end=str(index))
			else:
				graph.connect(start='root', end=str(index))

		return graph

	# nodes
	def __contains__(self, item: Union[str, Node]) -> bool:
		"""Checks if a node is in the graph.

		Args:
			item (Union[str, Node]): The item to check.

		Returns:
			bool: True if the item is in the graph, False otherwise.
		"""
		return item in self._nodes_dict

	@property
	def nodes_dict(self) -> Dict[str, Node]:
		"""Gets the dictionary of nodes in the graph.

		Returns:
			Dict[str, Node]: The nodes in the graph.
		"""
		return self._nodes_dict

	@property
	def nodes(self) -> List[Node]:
		"""Gets the list of nodes in the graph.

		Returns:
			List[Node]: The nodes in the graph.
		"""
		return list(self.nodes_dict.values())

	def get_node(self, node: Union[str, Node]) -> Node:
		"""
		Gets a node from the graph.

		Args:
			node (Union[str, Node]): The node to retrieve.

		Returns:
			Node: The retrieved node.

		Raises:
			TypeError: If the node type is not supported.
		"""
		if isinstance(node, (str, int)):
			return self.nodes_dict[node]
		elif isinstance(node, Node):
			return self.nodes_dict[node.id]
		else:
			raise TypeError(f'node of type {type(node)} is not supported!')

	def get_node_name(self, node: Union[str, Node]) -> str:
		"""
		Gets the name of a node.

		Args:
			node (Union[str, Node]): The node to retrieve the name from.

		Returns:
			str: The name of the node.

		Raises:
			TypeError: If the node type is not supported.
		"""
		if isinstance(node, (str, int)):
			return self.nodes_dict[node].id
		elif isinstance(node, Node):
			return node.id
		else:
			raise TypeError(f'node of type {type(node)} is not supported!')

	def generate_node_index(self) -> int:
		"""Generates a unique index for a new node.

		Returns:
			int: The generated index.
		"""
		index = self._node_counter
		self._node_counter += 1
		return index

	def add_node(self, name: str, label: Optional[str] = None, value: Optional[object] = None, style: Optional[NodeStyle] = None, if_node_exists: str = 'warn', **kwargs) -> Node:
		"""
		Adds a node to the graph.

		Args:
			name (str): The name of the new node.
			label (Optional[str]): A label for the node.
			value (Optional[object]): The value of the node.
			style (Optional[NodeStyle]): The style of the node.
			if_node_exists (str): What to do if a node with that name exists. One of 'warn', 'error', 'ignore'.
			**kwargs: Additional keyword arguments.

		Returns:
			Node: The created node.
		"""
		if isinstance(name, str):
			if name in self.nodes_dict:
				if if_node_exists == 'ignore':
					pass
				elif if_node_exists == 'warn':
					warnings.warn(f'Warning! A node with name "{name}" already exists in graph!')
				else:
					raise KeyError(f'duplicate node id:"{name}"!')

				node = self.get_node(node=name)
				if style is not None:
					node.style = style
				if label is not None:
					node.label = label
				if value is not None:
					node.value = value
				return node

			else:
				node = Node(
					name=name, graph=self, label=label, value=value,
					style=style, index=self.generate_node_index(), **kwargs
				)
				self.nodes_dict[name] = node
				return node
		elif isinstance(name, Node):
			node = name
			del name
			if node.id in self.nodes_dict:
				# if the node is already in the graph and node.graph is self then do nothing
				if node.graph is self and self.nodes_dict[node.id] is node:
					pass
				else:
					raise ValueError(f'node with id "{node.id}" is already in a graph!')
			else:
				if node.graph is not None:
					if node.graph is self:
						raise ValueError(f'node with id "{node.id}" is already in a graph but not in the graph dictionary: {self.nodes_dict.keys()}')
					else:
						raise ValueError(f'node with id "{node.id}" is already in a graph!')
				self.nodes_dict[node.id] = node
				return node
		else:
			raise TypeError(f'node of type {type(node)} is not supported!')

	def remove_node(self, node: Union[str, Node]):
		"""
		Removes a node from the graph.

		Args:
			node (Union[str, Node]): The node to remove.
		"""
		node = self.get_node(node=node)
		node.remove_edges()
		node._graph = None
		del self.nodes_dict[node.id]

	# edges
	@property
	def edges_dict(self) -> Dict[Tuple[str, str], Edge]:
		"""Gets the dictionary of edges in the graph.

		Returns:
			Dict[Tuple[str, str], Edge]: The edges in the graph.
		"""
		return {edge.id: edge for node in self.nodes for edge in node.outward_edges}

	@property
	def edges(self) -> List[Edge]:
		"""Gets the list of edges in the graph.

		Returns:
			List[Edge]: The edges in the graph.
		"""
		result = []
		for node in self.nodes:
			for edge in node.edges:
				if edge not in result:
					result.append(edge)
		return result

	def get_outward_edges(self, node: Union[str, Node]) -> List[Edge]:
		"""
		Gets the outward edges of a node.

		Args:
			node (Union[str, Node]): The node to get outward edges from.

		Returns:
			List[Edge]: The outward edges of the node.
		"""
		node = self.get_node(node=node)
		return node.outward_edges.copy()

	def get_inward_edges(self, node: Union[str, Node]) -> List[Edge]:
		"""
		Gets the inward edges of a node.

		Args:
			node (Union[str, Node]): The node to get inward edges from.

		Returns:
			List[Edge]: The inward edges of the node.
		"""
		node = self.get_node(node=node)
		return node.inward_edges.copy()

	def get_edges(self, node: Union[str, Node]) -> List[Edge]:
		"""
		Gets all edges of a node.

		Args:
			node (Union[str, Node]): The node to get edges from.

		Returns:
			List[Edge]: All edges of the node.
		"""
		return self.get_outward_edges(node=node)+self.get_inward_edges(node=node)

	def get_parents(self, node: Union[str, Node]) -> List[Node]:
		"""
		Gets the parents of a node.

		Args:
			node (Union[str, Node]): The node to get parents from.

		Returns:
			List[Node]: The parents of the node.
		"""
		return [inward_edge.start for inward_edge in self.get_inward_edges(node=node)]

	def num_parents(self, node: Union[str, Node]) -> int:
		"""
		Gets the number of parents of a node.

		Args:
			node (Union[str, Node]): The node to get the number of parents from.

		Returns:
			int: The number of parents.
		"""
		return len(self.get_parents(node=node))

	def has_parents(self, node: Union[str, Node]) -> bool:
		"""
		Checks if a node has parents.

		Args:
			node (Union[str, Node]): The node to check.

		Returns:
			bool: True if the node has parents, False otherwise.
		"""
		return self.num_parents(node=node) > 0

	@property
	def absolute_roots(self) -> List[Node]:
		"""Gets the absolute root nodes of the graph.

		Returns:
			List[Node]: The absolute root nodes.
		"""
		return [node for node in self.nodes if not node.has_parents()]

	@property
	def roots(self) -> List[Node]:
		"""Gets the root nodes of the graph.

		Returns:
			List[Node]: The root nodes.
		"""
		possible_roots = self.nodes.copy()
		for node in self.nodes:
			if node in possible_roots:
				for descendant in self.get_descendants(node=node, distance=False):
					if descendant in possible_roots:
						possible_roots.remove(descendant)
		return possible_roots

	def get_children(self, node: Union[str, Node]) -> List[Node]:
		"""
		Gets the children of a node.

		Args:
			node (Union[str, Node]): The node to get children from.

		Returns:
			List[Node]: The children of the node.
		"""
		return [outward_edge.end for outward_edge in self.get_outward_edges(node=node)]

	def num_children(self, node: Union[str, Node]) -> int:
		"""
		Gets the number of children of a node.

		Args:
			node (Union[str, Node]): The node to get the number of children from.

		Returns:
			int: The number of children.
		"""
		return len(self.get_children(node=node))

	def has_children(self, node: Union[str, Node]) -> bool:
		"""
		Checks if a node has children.

		Args:
			node (Union[str, Node]): The node to check.

		Returns:
			bool: True if the node has children, False otherwise.
		"""
		return self.num_children(node=node) > 0

	@property
	def leaves(self) -> List[Node]:
		"""Gets the leaf nodes of the graph.

		Returns:
			List[Node]: The leaf nodes.
		"""
		return [node for node in self.nodes if not node.has_children()]

	def _get_ancestors(self, node, nodes_travelled=None):
		"""
		:type node: Node or str
		:type nodes_travelled: list[Node] or None
		:rtype: list[Node]
		"""
		node = self.get_node(node)
		nodes_travelled = nodes_travelled or []
		nodes_travelled.append(node)
		parents = self.get_parents(node=node)
		if len(parents) == 0:
			return [], {}
		else:
			ancestors = []
			ancestors_dict = {1: []}
			for parent in parents:
				if parent not in ancestors:
					ancestors.append(parent)
					ancestors_dict[1].append(parent)

				if parent not in nodes_travelled:
					parent_ancestors, parent_ancestors_dict = self._get_ancestors(node=parent, nodes_travelled=nodes_travelled)
					for ancestor in parent_ancestors:
						if ancestor not in ancestors:
							ancestors.append(ancestor)
							for distance in parent_ancestors_dict.keys():
								ancestors_dict[distance+1] = parent_ancestors_dict[distance]
			return ancestors, ancestors_dict

	def get_ancestors(self, node, distance=True):
		"""
		:param Node or str node:
		:param bool distance: if True, ancestors and their respective distance to the node will be returned as dict
		:rtype: dict[int,list[Node]] or list[Node]
		"""
		ancestors, ancestors_dict = self._get_ancestors(node=node, nodes_travelled=None)
		if distance:
			return ancestors_dict
		else:
			return ancestors

	def is_node_in_loop(self, node):
		node = self.get_node(node)
		return node in self.get_ancestors(node=node, distance=False)

	def are_nodes_in_same_loop(self, node1, node2):
		node1 = self.get_node(node1)
		node2 = self.get_node(node2)
		node1_is_ancestor_to_node2 = node1 in self.get_ancestors(node=node2, distance=False)
		node2_is_ancestor_to_node1 = node2 in self.get_ancestors(node=node1, distance=False)
		return node1_is_ancestor_to_node2 and node2_is_ancestor_to_node1

	@property
	def loop_nodes(self):
		"""
		:rtype: list[Node]
		"""
		return [node for node in self.nodes if node.is_in_loop()]

	def _get_descendants(self, node, nodes_travelled=None):
		"""
		:type node: Node or str
		:type nodes_travelled: list[Node] or None
		:rtype: list[Node]
		"""
		node = self.get_node(node)
		nodes_travelled = nodes_travelled or []
		nodes_travelled.append(node)
		children = self.get_children(node=node)
		if len(children) == 0:
			return [], {}
		else:
			descendants = []
			descendants_dict = {1: []}
			for child in children:
				if child not in nodes_travelled:
					if child not in descendants:
						descendants.append(child)
						descendants_dict[1].append(child)
					child_descendants, child_descendants_dict = self._get_descendants(node=child, nodes_travelled=nodes_travelled)
					for descendant in child_descendants:
						if descendant not in descendants:
							descendants.append(descendant)
							for distance in child_descendants_dict.keys():
								descendants_dict[distance+1] = child_descendants_dict[distance]
			return descendants, descendants_dict

	def get_descendants(self, node, distance=True):
		"""
		:param Node or str node:
		:param bool distance: if True, descendants and their respective distance to the node will be returned as dict
		:rtype: dict[int,list[Node]] or list[Node]
		"""
		descendants, descendants_dict = self._get_descendants(node=node, nodes_travelled=None)
		if distance:
			return descendants_dict
		else:
			return descendants

	def get_siblings(self, node):
		"""
		:type node: Node or str
		:rtype: list[Node]
		"""
		node = self.get_node(node)
		parents = self.get_parents(node=node)
		siblings = []
		for parent in parents:
			for parents_child in self.get_children(node=parent):
				if parents_child not in siblings and parents_child != node:
					siblings.append(parents_child)
		return siblings

	def num_siblings(self, node):
		"""
		:type node: Node or str
		:rtype: int
		"""
		return len(self.get_siblings(node=node))

	def has_siblings(self, node):
		"""
		:type node: Node or str
		:rtype: bool
		"""
		return self.num_siblings(node=node) > 0

	def get_spouses(self, node):
		"""
		:type node: Node or str
		:rtype: list[Node]
		"""
		node = self.get_node(node)
		children = self.get_children(node=node)
		spouses = []
		for child in children:
			for childs_parent in self.get_parents(node=child):
				if childs_parent not in spouses and childs_parent != node:
					spouses.append(childs_parent)
		return spouses

	def num_spouses(self, node):
		"""
		:type node: Node or str
		:rtype: int
		"""
		return len(self.get_spouses(node=node))

	def has_spouses(self, node):
		"""
		:type node: Node or str
		:rtype: bool
		"""
		return self.num_spouses(node=node) > 0

	def get_tree_str(self):
		"""
		returns a tree representation of the graph as a string
 		:rtype: str
		"""
		already_added = []
		tree_strings = []
		for root in self.roots:
			tree_string = root.get_tree_str(already_added=already_added)
			tree_strings.append(tree_string)
		return '\n'.join(tree_strings)

	def connect(self, start: Union[str, Node], end: Union[str, Node], id: Optional[str] = None, label: Optional[str] = None, value: Optional[object] = None, style: Optional[EdgeStyle] = None, if_edge_exists: str = 'warn', **kwargs) -> Edge:
		"""
		Connects two nodes in the graph.

		Args:
			start (Union[str, Node]): The starting node.
			end (Union[str, Node]): The ending node.
			id (Optional[str]): The ID of the edge.
			label (Optional[str]): The label of the edge.
			value (Optional[object]): The value of the edge.
			style (Optional[EdgeStyle]): The style of the edge.
			if_edge_exists (str): What to do if an edge with that ID exists. One of 'warn', 'error', 'ignore'.
			**kwargs: Additional keyword arguments.

		Returns:
			Edge: The created edge.
		"""
		start = self.get_node(node=start)
		end = self.get_node(node=end)
		edge_id = (start.id, end.id, id)

		if edge_id not in start.outward_edge_ids and edge_id not in end.inward_edge_ids:
			edge = Edge(graph=self, start=start, end=end, id=id, value=value, label=label, style=style, **kwargs)

		elif edge_id in start.outward_edge_ids and edge_id in end.inward_edge_ids:
			if if_edge_exists == 'ignore':
				pass
			elif if_edge_exists == 'warn':
				warnings.warn(f'Warning! Edge: {edge_id} already exists!')
			else:
				raise ValueError(f'Error! Edge {edge_id} already exists!')

			edge = start.get_outward_edge(id=edge_id)
			if style is not None:
				edge.style = style
			if label is not None:
				edge.label = label
			if value is not None:
				edge.value = value

		elif edge_id in start.outward_edges and edge_id not in end.inward_edges:
			raise ValueError(
				f'This is very weird! Edge {edge_id} already in the outward edges of start node '
				f'but not the inward edges of the end node!'
			)

		else:
			raise ValueError(
				f'This is very weird! Edge {edge_id} already in the inward edges of end node '
				f'but not the outward edges of the start node!'
			)

		return edge

	@staticmethod
	def disconnect(edge: Edge):
		"""
		Disconnects an edge from the graph.

		Args:
			edge (Edge): The edge to disconnect.
		"""
		edge.start.remove_outward_edge(edge_id=edge.id)
		edge.end.remove_inward_edge(edge_id=edge.id)
		edge._raw_id = (None, None, None)
		edge._graph = None

	# similarity
	def is_similar_to(self, other: 'BasicGraph') -> bool:
		"""
		Checks if this graph is similar to another graph.

		Args:
			other (BasicGraph): The other graph to compare.

		Returns:
			bool: True if similar, False otherwise.
		"""
		if len(self._nodes_dict) != len(other._nodes_dict):
			return False

		for name, node in self._nodes_dict.items():
			other_node = other._nodes_dict[name]
			if not node.is_similar_to(other=other_node):
				return False

		if self._is_strict != other._is_strict:
			return False

		if self._ordering != other._ordering:
			return False

		return True
