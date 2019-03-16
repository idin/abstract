from .GraphObj import GraphObj
from .Style import NodeStyle

from collections import OrderedDict

CORNER = u'\u2514'
TWO_WAY = u'\u251C'
HORIZONTAL = u'\u2500'
VERTICAL = u'\u2502'


class Node(GraphObj):
	def __init__(self, graph, name, value=None, label=None, style=None, **kwargs):
		style = style or NodeStyle()
		super().__init__(graph=graph, id=name, value=value, label=label, style=style, **kwargs)
		self._outward_edges_dict = OrderedDict()
		self._inward_edges_dict = OrderedDict()

	@property
	def name(self):
		return self.id

	@property
	def outward_edge_ids(self):
		return list(self._outward_edges_dict.keys())

	@property
	def inward_edge_ids(self):
		return list(self._inward_edges_dict.keys())

	def get_outward_edge(self, id):
		return self._outward_edges_dict[id]

	def get_inward_edge(self, id):
		return self._inward_edges_dict[id]

	def append_outward_edge(self, edge):
		"""
		:type edge: GraphObj
		"""
		self._outward_edges_dict[edge.id] = edge

	def append_inward_edge(self, edge):
		"""
		:type edge: GraphObj
		"""
		self._inward_edges_dict[edge.id] = edge

	def remove_outward_edge(self, edge):
		del self._outward_edges_dict[edge.id]

	def remove_inward_edge(self, edge):
		del self._inward_edges_dict[edge.id]

	@property
	def label(self):
		result = self._label or str(self.id)
		return result.replace('"', '\\"')

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
	def anscestors(self):
		"""
		:rtype: list[Node]
		"""
		return self.graph._get_ancestors(node=self)

	@property
	def descendants(self):
		"""
		:rtype: list[Node]
		"""
		return self.graph._get_descendants(node=self)

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
		for edge in self._outward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		for edge in self._outward_edges_dict.values():
			if edge not in result:
				result.append(edge)
		return result

	def remove_edges(self):
		for edge in self.edges:
			edge.remove_self()









