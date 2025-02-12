from ._GraphObj import GraphObj
from .styling.NodeStyle import NodeStyle
from typing import Optional, Union, List, Dict


CORNER = u'\u2514'
TWO_WAY = u'\u251C'
HORIZONTAL = u'\u2500'
VERTICAL = u'\u2502'


class Node(GraphObj):
	def __init__(
			self, graph: 'Graph', name: str, value: Optional[object] = None, 
			label: Optional[str] = None, tooltip: Optional[str] = None, 
			style: Optional[NodeStyle] = None, index: int = 0, **kwargs
	):
		"""
		Initializes a Node instance.

		Args:
			graph (Graph): The graph this node belongs to.
			name (str): Name of the node (code friendly, no weird characters, etc.) it should be unique in the graph.
			value (Optional[object]): Any object stored in the node.
			label (Optional[str]): A more presentable/user-friendly name.
			tooltip (Optional[str]): Tooltip for the node.
			style (Optional[NodeStyle]): Style for the node.
			index (int): Index of the node.
			**kwargs: Additional keyword arguments.
		"""

		super().__init__(
			graph=graph, id=name, value=value, label=label, tooltip=tooltip, style=style,
			# additional_styling_function=additional_styling_function,
			**kwargs
		)
		self._outward_edges_dict = dict()
		self._inward_edges_dict = dict()
		self._outward_edges_have_start_node = True
		self._inward_edges_have_end_node = True
		self._index = index
		graph._nodes_dict[name] = self

	# make node hashable
	def __hash__(self):
		return hash(self.id)

	@property
	def style(self) -> Optional[NodeStyle]:
		"""
		Gets the style of the node.

		Returns:
			Optional[NodeStyle]: The style of the node.
		"""
		return self._style

	@style.setter
	def style(self, style: Union[NodeStyle, Dict]):
		"""
		Sets the style of the node.

		Args:
			style (Union[NodeStyle, Dict]): The style to set, can be a NodeStyle instance or a dictionary.
		
		Raises:
			RuntimeError: If overwriting the style is not allowed.
			TypeError: If the style type is not supported.
		"""
		if self._style is not None and not self.graph._style_overwrite_allowed:
			raise RuntimeError('Cannot overwrite node style!')

		if isinstance(style, dict):
			self._style = NodeStyle(**style)
		elif isinstance(style, NodeStyle):
			self._style = style
		elif style is None:
			pass
		else:
			raise TypeError(f'node style of type {type(style)} is not supported!')

	@property
	def index(self) -> int:
		"""Gets the index of the node."""
		return self._index

	def __getstate__(self) -> Dict:
		"""Returns the state of the node for pickling."""
		state = super().__getstate__()
		state.update({
			'outward_edges_dict': self._outward_edges_dict,
			'inward_edges_dict': self._inward_edges_dict,
			'index': self._index
		})
		return state

	def __setstate__(self, state: Dict):
		"""Restores the state of the node from a pickled state."""
		super().__setstate__(state=state)
		self._outward_edges_dict = state['outward_edges_dict']
		self._inward_edges_dict = state['inward_edges_dict']
		self._outward_edges_have_start_node = False
		self._inward_edges_have_end_node = False
		self._index = state['index']

	def is_similar_to(self, other: 'Node') -> bool:
		"""
		Checks if this node is similar to another node.

		Args:
			other (Node): The other node to compare.

		Returns:
			bool: True if similar, False otherwise.
		"""
		if not super().is_similar_to(other=other):
			return False
		if len(self._outward_edges_dict) != len(other._outward_edges_dict):
			return False
		if len(self._inward_edges_dict) != len(other._inward_edges_dict):
			return False
		for id, outward_edge in self._outward_edges_dict.items():
			other_outward_edge = other._outward_edges_dict[id]
			if not outward_edge.is_similar_to(other=other_outward_edge):
				return False
		for id, inward_edge in self._inward_edges_dict.items():
			other_inward_edge = other._inward_edges_dict[id]
			if not inward_edge.is_similar_to(other=other_inward_edge):
				return False
		return True

	def update_edges(self):
		"""Updates the edges of the node."""
		if not self._outward_edges_have_start_node:
			for outward_edge in self._outward_edges_dict.values():
				outward_edge._start = self
				outward_edge._graph = self.graph
		self._outward_edges_have_start_node = True
		if not self._inward_edges_have_end_node:
			for inward_edge in self._inward_edges_dict.values():
				inward_edge._end = self
				inward_edge._graph = self.graph
		self._inward_edges_have_end_node = True

	@property
	def outward_edges_dict(self) -> Dict[str, 'GraphObj']:
		"""Gets the outward edges dictionary."""
		return self._outward_edges_dict

	@property
	def inward_edges_dict(self) -> Dict[str, 'GraphObj']:
		"""Gets the inward edges dictionary."""
		return self._inward_edges_dict

	@property
	def name(self) -> str:
		"""Gets the name of the node."""
		return self.id

	@property
	def outward_edge_ids(self) -> List[str]:
		"""Gets the outward edge IDs."""
		return list(self.outward_edges_dict.keys())

	@property
	def inward_edge_ids(self) -> List[str]:
		"""Gets the inward edge IDs."""
		return list(self.inward_edges_dict.keys())

	def get_outward_edge(self, id: str) -> 'GraphObj':
		"""
		Gets an outward edge by ID.

		Args:
			id (str): The ID of the outward edge.

		Returns:
			GraphObj: The outward edge.
		"""
		return self.outward_edges_dict[id]

	def get_inward_edge(self, id: str) -> 'GraphObj':
		"""
		Gets an inward edge by ID.

		Args:
			id (str): The ID of the inward edge.

		Returns:
			GraphObj: The inward edge.
		"""
		return self.inward_edges_dict[id]

	def append_outward_edge(self, edge: 'GraphObj'):
		"""
		Appends an outward edge to the node.

		Args:
			edge (GraphObj): The edge to append.
		"""
		self.outward_edges_dict[edge.id] = edge

	def append_inward_edge(self, edge: 'GraphObj'):
		"""
		Appends an inward edge to the node.

		Args:
			edge (GraphObj): The edge to append.
		"""
		self.inward_edges_dict[edge.id] = edge

	def remove_outward_edge(self, edge_id: str):
		"""Removes an outward edge by ID."""
		del self.outward_edges_dict[edge_id]

	def remove_inward_edge(self, edge_id: str):
		"""Removes an inward edge by ID."""
		del self.inward_edges_dict[edge_id]

	@property
	def label(self) -> str:
		"""Gets the label of the node."""
		if self._label:
			result = str(self._label)
		else:
			result = str(self.id)
		return result.replace('"', '\\"')

	@label.setter
	def label(self, label: str):
		"""Sets the label of the node."""
		self._label = label

	@property
	def _label_converter(self):
		"""Gets the label converter for the node."""
		return self.graph._node_label_converter

	def __str__(self) -> str:
		"""Returns a string representation of the node."""
		return f'Node:{self.id}'

	def __repr__(self) -> str:
		"""Returns a string representation of the node for debugging."""
		return str(self)

	def __lt__(self, other: 'Node') -> bool:
		"""Less than comparison for sorting nodes."""
		return (self.index, self.name) < (other.index, other.name)

	def __gt__(self, other: 'Node') -> bool:
		"""Greater than comparison for sorting nodes."""
		return (self.index, self.name) > (other.index, other.name)

	def __le__(self, other: 'Node') -> bool:
		"""Less than or equal comparison for sorting nodes."""
		return (self.index, self.name) <= (other.index, other.name)

	def __ge__(self, other: 'Node') -> bool:
		"""Greater than or equal comparison for sorting nodes."""
		return (self.index, self.name) >= (other.index, other.name)

	def __eq__(self, other: 'Node') -> bool:
		"""Equality comparison for nodes."""
		if not isinstance(other, Node):
			raise TypeError(f'node of type {type(other)} is not supported!')
		return (self.index, self.name) == (other.index, other.name)

	def __ne__(self, other: 'Node') -> bool:
		"""Inequality comparison for nodes."""
		if not isinstance(other, Node):
			raise TypeError(f'node of type {type(other)} is not supported!')
		return (self.index, self.name) != (other.index, other.name)

	def get_tree_str(self, indentation: str = '', already_added: Optional[List['Node']] = None) -> str:
		"""
		Gets a string representation of the node's tree structure.

		Args:
			indentation (str): The indentation for the tree structure.
			already_added (Optional[List[Node]]): Nodes that have already been added to avoid cycles.

		Returns:
			str: The tree structure as a string.
		"""
		if already_added is None:
			already_added = []

		tree_string = self.label

		if self in already_added:
			tree_string += '*\n'

		else:
			tree_string += '\n'
			num_children = len(self.children)

			for child_num, child in enumerate(self.children):

				already_added.append(self)
				if child_num+1 == num_children:
					tree_string += indentation + CORNER + ' ' + child.get_tree_str(
						indentation=indentation + '  ', already_added=already_added
					)

				else:
					tree_string += indentation + TWO_WAY + ' ' + child.get_tree_str(
						indentation=indentation + VERTICAL + ' ', already_added=already_added
					)

		return tree_string

	def get_graphviz_str(self) -> str:
		"""
		Gets the Graphviz string representation of the node.

		Returns:
			str: The Graphviz representation.
		"""

		parts = [f'label="{self.display_label()}"']

		if self._tooltip is not None:
			parts.append(f'tooltip="{self._tooltip}"')

		style = self.style
		if style is not None:
			parts.append(style.get_graphviz_str())

		return f'"{self.id}" [' + ' '.join(parts) + ']'

	def connect_to(self, node: 'Node', **kwargs) -> 'GraphObj':
		"""
		Connects this node to another node.

		Args:
			node (Node): The node to connect to.
			**kwargs: Additional keyword arguments.

		Returns:
			GraphObj: The resulting graph object.
		"""
		return self.graph.connect(start=self, end=node, **kwargs)

	def connect_from(self, node: 'Node', **kwargs) -> 'GraphObj':
		"""
		Connects another node to this node.

		Args:
			node (Node): The node to connect from.
			**kwargs: Additional keyword arguments.

		Returns:
			GraphObj: The resulting graph object.
		"""
		return self.graph.connect(start=node, end=self, **kwargs)

	@property
	def parents(self) -> List['Node']:
		"""Gets the parents of the node."""
		return self.graph.get_parents(node=self)
	
	@property
	def siblings(self) -> List['Node']:
		"""Gets the siblings of the node."""
		siblings = {}
		for parent in self.parents:
			for child in parent.children:
				if child.id not in siblings and child != self:
					siblings[child.id] = child
		return list(siblings.values())
	
	@property
	def co_parents(self) -> List['Node']:
		"""Gets the co-parents of the node. (spouses)"""
		co_parents = {}
		for child in self.children:
			for parent in child.parents:
				if parent.id not in co_parents and parent != self:
					co_parents[parent.id] = parent
		return list(co_parents.values())

	def has_parents(self) -> List['Node']:
		"""Checks if the node has parents."""
		return self.graph.get_parents(node=self)

	def get_child_rank(self, parent: 'Node') -> int:
		"""
		Returns the rank of this node in terms of its index relative to its siblings.

		Args:
			parent (Node): The parent node.

		Returns:
			int: The rank of this node.

		Raises:
			ValueError: If this node is not a child of the parent.
		"""
		siblings = parent.children
		if self not in siblings:
			raise ValueError(f'{self} is not a child of {parent}')
		return sorted(siblings).index(self)

	@property
	def children(self) -> List['Node']:
		"""Gets the children of the node."""
		return self.graph.get_children(node=self)

	def has_children(self) -> bool:
		"""Checks if the node has children."""
		return self.graph.has_children(node=self)

	@property
	def ancestors(self) -> List['Node']:
		"""Gets the ancestors of the node."""
		return self.graph.get_ancestors(node=self, distance=False)

	@property
	def descendants(self) -> List['Node']:
		"""Gets the descendants of the node."""
		return self.graph.get_descendants(node=self, distance=False)

	@property
	def num_descendants(self) -> int:
		"""Gets the number of descendants of the node."""
		return len(self.descendants)

	@property
	def outward_edges(self) -> List['Edge']:
		"""Gets the outward edges of the node."""
		result = []
		for edge in self._outward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	@property
	def inward_edges(self) -> List['Edge']:
		"""Gets the inward edges of the node."""
		result = []
		for edge in self._inward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	@property
	def edges(self) -> List['Edge']:
		"""Gets all edges of the node."""
		result = []
		for edge in self.outward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		for edge in self.inward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	def remove_edges(self):
		"""Removes all edges from the node."""
		for edge in self.edges:
			edge.remove_self()

	@property
	def num_outward_edges(self) -> int:
		"""Gets the number of outward edges."""
		return len(self.outward_edges_dict)

	def is_in_loop(self) -> bool:
		"""Checks if the node is in a loop."""
		return self.graph.is_node_in_loop(node=self)

	def is_in_loop_with(self, other: 'Node') -> bool:
		"""Checks if this node is in a loop with another node."""
		return self.graph.are_nodes_in_same_loop(node1=self, node2=other)
