from ._GraphObj import GraphObj
from .graph_style.GraphObjStyle import NodeStyle


CORNER = u'\u2514'
TWO_WAY = u'\u251C'
HORIZONTAL = u'\u2500'
VERTICAL = u'\u2502'


class Node(GraphObj):
	def __init__(self, graph, name, value=None, label=None, style=None, index=0, **kwargs):
		"""
		:param .Graph.Graph graph: the graph this node belongs to
		:param str name: name of the node (code friendly, no weird characters, etc.) it should be unique in the graph
		:param value: any object stored in the node
		:param str label: a more presentable/user-friendly name
		:param style:
		:param kwargs:
		"""
		super().__init__(graph=graph, id=name, value=value, label=label, style=style, **kwargs)
		self._outward_edges_dict = dict()
		self._inward_edges_dict = dict()
		self._outward_edges_have_start_node = True
		self._inward_edges_have_end_node = True
		self._index = index

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

	@property
	def style(self):
		"""
		:rtype: NodeStyle
		"""
		if self._style is None:
			return self.graph.style.get_node_style(style_name='default', node_name=self.name)
		elif isinstance(self._style, str):
			return self.graph.style.get_node_style(style_name=self._style, node_name=self.name)
		else:
			raise TypeError(f'{self}._style is of type {type(self._style)}')

	@style.setter
	def style(self, style):
		"""
		:type style: NodeStyle or NoneType or dict
		"""
		if style is None:
			self._style = None
		else:
			if isinstance(style, dict):
				the_style = NodeStyle(**style)
			elif isinstance(style, NodeStyle):
				the_style = style.copy()
			elif isinstance(style, str):

				the_style = self.graph.style.node_styles[style]
			else:
				raise TypeError(f'node.style is of type {type(style)}')

			if the_style.name is None:
				the_style._name = self.name
			if the_style.name not in self.graph.style.node_styles:
				self.graph.style.node_styles[the_style.name] = []
			self.graph.style.node_styles[the_style.name].append(the_style)
			self._style = the_style.name

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
		if self.style is None:
			return f'"{self.id}" [label="{self.label}" '
		else:
			return f'"{self.id}" [label="{self.label}" ' + self.style.get_graphviz_str() + ']'

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
