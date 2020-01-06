from ._GraphObj import GraphObj
from .graph_style.NodeStyle import NodeStyle


CORNER = u'\u2514'
TWO_WAY = u'\u251C'
HORIZONTAL = u'\u2500'
VERTICAL = u'\u2502'


class Node(GraphObj):
	def __init__(
			self, graph, name, value=None, label=None, style=None, index=0,
			**kwargs
	):
		"""
		:param .Graph.Graph graph: the graph this node belongs to
		:param str name: name of the node (code friendly, no weird characters, etc.) it should be unique in the graph
		:param value: any object stored in the node
		:param str label: a more presentable/user-friendly name
		:param style:
		:param kwargs:
		"""
		style = style or NodeStyle()

		super().__init__(
			graph=graph, id=name, value=value, label=label, style=style,
			# additional_styling_function=additional_styling_function,
			**kwargs
		)
		self._outward_edges_dict = dict()
		self._inward_edges_dict = dict()
		self._outward_edges_have_start_node = True
		self._inward_edges_have_end_node = True
		self._index = index

	@property
	def style(self):
		"""
		:rtype: NodeStyle
		"""
		return self._style

	@style.setter
	def style(self, style):
		"""
		:type style: NodeStyle or dict
		"""
		if isinstance(style, dict):
			style = NodeStyle(**style)
		self._style = style
		# self._style_is_native = style is not None

	@property
	def index(self):
		return self._index

	def __getstate__(self):
		state = super().__getstate__()
		state.update({
			'outward_edges_dict': self._outward_edges_dict,
			'inward_edges_dict': self._inward_edges_dict,
			'index': self._index
		})
		return state

	def __setstate__(self, state):
		super().__setstate__(state=state)
		self._outward_edges_dict = state['outward_edges_dict']
		self._inward_edges_dict = state['inward_edges_dict']
		self._outward_edges_have_start_node = False
		self._inward_edges_have_end_node = False
		self._index = state['index']

	def is_similar_to(self, other):
		"""
		:type other: Node
		:rtype: bool
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
	def outward_edges_dict(self):
		return self._outward_edges_dict

	@property
	def inward_edges_dict(self):
		return self._inward_edges_dict

	@property
	def name(self):
		return self.id

	@property
	def outward_edge_ids(self):
		return list(self.outward_edges_dict.keys())

	@property
	def inward_edge_ids(self):
		return list(self.inward_edges_dict.keys())

	def get_outward_edge(self, id):
		return self.outward_edges_dict[id]

	def get_inward_edge(self, id):
		return self.inward_edges_dict[id]

	def append_outward_edge(self, edge):
		"""
		:type edge: GraphObj
		"""
		self.outward_edges_dict[edge.id] = edge

	def append_inward_edge(self, edge):
		"""
		:type edge: GraphObj
		"""
		self.inward_edges_dict[edge.id] = edge

	def remove_outward_edge(self, edge_id):
		del self.outward_edges_dict[edge_id]

	def remove_inward_edge(self, edge_id):
		del self.inward_edges_dict[edge_id]

	@property
	def label(self):
		if self._label:
			result = str(self.raw_label)
		else:
			result = str(self.id)
		return result.replace('"', '\\"')

	@label.setter
	def label(self, label):
		self._label = label

	def __str__(self):
		return f'Node:{self.id}'

	def __repr__(self):
		return str(self)

	def __lt__(self, other):
		"""
		:type other: Node
		:rtype: bool
		"""
		return (self.index, self.name) < (other.index, other.name)

	def __gt__(self, other):
		"""
		:type other: Node
		:rtype: bool
		"""
		return (self.index, self.name) > (other.index, other.name)

	def __le__(self, other):
		"""
		:type other: Node
		:rtype: bool
		"""
		return (self.index, self.name) <= (other.index, other.name)

	def __ge__(self, other):
		"""
		:type other: Node
		:rtype: bool
		"""
		return (self.index, self.name) >= (other.index, other.name)

	def __eq__(self, other):
		"""
		:type other: Node
		:rtype: bool
		"""
		return (self.index, self.name) == (other.index, other.name)

	def __ne__(self, other):
		"""
		:type other: Node
		:rtype: bool
		"""
		return (self.index, self.name) != (other.index, other.name)

	def get_tree_str(self, indentation='', already_added=None):
		"""
		:rtype: str
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

	def get_graphviz_str(self):
		"""
		:rtype: str
		"""
		style = self.style

		if style is None:
			return f'"{self.id}" [label="{self.label}"]'

		else:
			return f'"{self.id}" [label="{self.label}" ' + style.get_graphviz_str() + ']'

	def connect_to(self, node, **kwargs):
		"""
		:type node: Node
		:rtype: GraphObj
		"""
		return self.graph.connect(start=self, end=node, **kwargs)

	def connect_from(self, node, **kwargs):
		"""
		:type node:
		:rtype:
		"""
		return self.graph.connect(start=node, end=self, **kwargs)

	@property
	def parents(self):
		"""
		:rtype: list[Node]
		"""
		return self.graph.get_parents(node=self)

	def has_parents(self):
		return self.graph.get_parents(node=self)

	def get_child_rank(self, parent):
		"""
		returns the rank of this node in terms of its index relative to its siblings, rank starts from 0
		:type parent: Node
		:rtype: int
		"""
		siblings = parent.children
		if self not in siblings:
			ValueError(f'{self} is not a child of {parent}')
		return sorted(siblings).index(self)

	@property
	def children(self):
		"""
		:rtype: list[Node]
		"""
		return self.graph.get_children(node=self)

	def has_children(self):
		return self.graph.has_children(node=self)

	@property
	def ancestors(self):
		"""
		:rtype: list[Node]
		"""
		return self.graph.get_ancestors(node=self, distance=False)

	@property
	def descendants(self):
		"""
		:rtype: list[Node]
		"""
		return self.graph.get_descendants(node=self, distance=False)

	@property
	def num_descendants(self):
		"""
		:rtype: int
		"""
		return len(self.descendants)

	@property
	def outward_edges(self):
		"""
		:rtype: list[Edge]
		"""
		result = []
		for edge in self._outward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	@property
	def inward_edges(self):
		"""
		:rtype: list[Edge]
		"""
		result = []
		for edge in self._inward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	@property
	def edges(self):
		"""
		:rtype: list[Edge]
		"""
		result = []
		for edge in self.outward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		for edge in self.inward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	def remove_edges(self):
		for edge in self.edges:
			edge.remove_self()

	@property
	def num_outward_edges(self):
		return len(self.outward_edges_dict)

	def is_in_loop(self):
		return self.graph.is_node_in_loop(node=self)

	def is_in_loop_with(self, other):
		return self.graph.are_nodes_in_same_loop(node1=self, node2=other)
