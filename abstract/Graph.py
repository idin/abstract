from .Node import Node
from .Edge import Edge
from collections import OrderedDict
import graphviz
from .Style import NodeStyle
from .get_ancestors import get_ancestors
from .get_descendants import get_descendants

import os


class Graph:
	def __init__(self, obj=None, strict=True, ordering=True):
		self._nodes = OrderedDict()
		self._is_strict = strict
		self._ordering = ordering

		# if a dictionary or an object with a __graph_dict__() method is passed use that to create the graph
		if obj:
			self.append(obj=obj)

	@property
	def nodes(self):
		"""
		:rtype: list[Node]
		"""
		return list(self._nodes.values())

	@property
	def edges(self):
		"""
		:rtype: list[Edge]
		"""
		result = []
		for node in self.nodes:
			for edge in node.edges:
				if edge not in result:
					result.append(edge)
		return result

	def get_tree_str(self):
		"""
		:rtype: str
		"""
		already_added = []
		tree_strings = []
		for root in self.roots:
			tree_string = root.get_tree_str(already_added=already_added)
			tree_strings.append(tree_string)
		return '\n'.join(tree_strings)

	@property
	def _graphviz_header(self):
		if self._is_strict:
			first_part = 'strict digraph G {\n'
		else:
			first_part = 'digraph G{\n'

		if self._ordering:
			second_part = ''
		else:
			second_part = '\tordering=out;\n'
		return first_part+second_part

	def get_graphviz_str(self):
		nodes_str = '\t{\n\t\t' + '\n\t\t'.join([node.get_graphviz_str() for node in self._nodes.values()]) + '\n\t}\n'
		edges_str = '\t' + '\n\t'.join([edge.get_graphviz_str() for edge in self.edges]) + '\n'
		return self._graphviz_header + nodes_str + edges_str + '}'

	def render(self, path=None, view=True):

		if path is None:
			return graphviz.Source(source=self.get_graphviz_str())
		else:
			filename, file_extension = os.path.splitext(path)
			output_format = file_extension.lstrip('.')
			source = graphviz.Source(source=self.get_graphviz_str(), format=output_format)
			return source.render(filename=filename, view=view)

	draw = render

	def get_node(self, node):
		"""
		:type node: Node or str
		:rtype: Node
		"""
		if isinstance(node, str):
			return self._nodes[node]
		else:
			return self._nodes[node.id]

	def get_node_name(self, node):
		"""
		:type node: Node or str
		:rtype: Node
		"""
		if isinstance(node, str):
			return self._nodes[node].id
		else:
			return node.id

	def get_outward_edges(self, node):
		"""
		:type node: Node or str
		:rtype: list[Edge]
		"""
		node = self.get_node(node=node)
		return node.outward_edges.copy()

	def get_inward_edges(self, node):
		"""
		:type node: Node or str
		:rtype: list[Edge]
		"""
		node = self.get_node(node=node)
		return node.inward_edges.copy()

	def get_edges(self, node):
		"""
		:type node: Node or str
		:rtype: list[Edge]
		"""
		return self.get_outward_edges(node=node)+self.get_inward_edges(node=node)

	def get_parents(self, node):
		"""
		:type node: Node or str
		:rtype: list[Node]
		"""
		return [inward_edge.start for inward_edge in self.get_inward_edges(node=node)]

	def has_parents(self, node):
		"""
		:type node: Node or str
		:rtype: Node
		"""
		return len(self.get_parents(node=node))

	@property
	def absolute_roots(self):
		"""
		:rtype: list[Node]
		"""
		return [node for node in self.nodes if not node.has_parents()]

	@property
	def roots(self):
		"""
		:rtype: list[Node]
		"""
		possible_roots = self.nodes.copy()
		for node in self.nodes:
			if node in possible_roots:
				for descendant in self.get_descendants(node=node, distance=False):
					if descendant in possible_roots:
						possible_roots.remove(descendant)
		return possible_roots

	def get_children(self, node):
		"""
		:type node: Node or str
		:rtype: list[Node]
		"""
		return [outward_edge.end for outward_edge in self.get_outward_edges(node=node)]

	def has_children(self, node):
		"""
		:type node: Node or str
		:rtype: Node
		"""
		return len(self.get_children(node=node))

	@property
	def leaves(self):
		"""
		:rtype: list[Node]
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
				if parent not in nodes_travelled:
					if parent not in ancestors:
						ancestors.append(parent)
						ancestors_dict[1].append(parent)
					parent_ancestors, parent_ancestors_dict = self._get_ancestors(node=parent, nodes_travelled=nodes_travelled)
					for ancestor in parent_ancestors:
						if ancestor not in ancestors:
							ancestors.append(ancestor)
							for distance in parent_ancestors_dict.keys():
								ancestors_dict[distance+1] = parent_ancestors_dict[distance]
			return ancestors, ancestors_dict

	def get_ancestors(self, node, distance=True):
		ancestors, ancestors_dict = self._get_ancestors(node=node, nodes_travelled=None)
		if distance:
			return ancestors_dict
		else:
			return ancestors

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

	def add_node(self, name, label=None, value=None, style=None, if_node_exists='warn', **kwargs):
		"""
		:param str name: name of the new node
		:param str or NoneType label: a label for the node
		:param value: node value
		:param NodeStyle style: style of the node
		:param str if_node_exists: what to do if a node with that name exists. One of 'warn', 'error', 'ignore'
		:param kwargs:
		:rtype: Node
		"""
		if name in self._nodes:
			if if_node_exists == 'error':
				raise KeyError(f'duplicate node id:"{id}"!')
			else:
				node = self.get_node(node=name)
				if if_node_exists != 'ignore':
					print(f'Warning! A node with name "{id}" already exists in graph!')
				if style is not None:
					node.style = style
				return node

		else:
			node = Node(name=name, graph=self, label=label, value=value, style=style, **kwargs)
			self._nodes[name] = node
			return node

	def connect(self, start, end, id=None, label=None, value=None, style=None, if_edge_exists='warn', **kwargs):
		"""
		:param Node or str start: starting node
		:param Node or str end: end node
		:param id:
		:param label:
		:param value:
		:param style:
		:param if_edge_exists:
		:param kwargs:
		:return:
		"""
		start = self.get_node(node=start)
		end = self.get_node(node=end)

		edge_id = (start.id, end.id, id)
		if edge_id in start.outward_edge_ids and edge_id in end.inward_edge_ids:
			if if_edge_exists == 'error':
				raise ValueError(f'Error! Edge {edge_id} already exists!')
			elif if_edge_exists != 'ignore':
				print(f'Warning! Edge: {edge_id} already exists!')
			edge = start.get_outward_edge(id=edge_id)
			if style is not None:
				edge.style = style
			if label is not None:
				edge.label = label
			if value is not None:
				edge.value = value

		elif edge_id not in start.outward_edge_ids and edge_id not in end.inward_edge_ids:
			edge = Edge(graph=self, start=start, end=end, id=id, value=value, label=label, style=style, **kwargs)

		else:
			raise ValueError(f'Error! Edge {edge_id} has a different start or end!')

		return edge

	@staticmethod
	def disconnect(edge):
		"""
		:type edge: Edge
		"""
		edge.start.remove_outward_edge(edge=edge)
		edge.end.remove_inward_edge(edge=edge)
		edge._id = (None, None, None)
		edge._graph = None

	def remove_node(self, node):
		"""
		:type node: Node or str
		"""
		node = self.get_node(node=node)
		node.remove_edges()
		node._graph = None
		del self._nodes[node.id]

	@classmethod
	def from_lists(
			cls, start, end, edge,
			strict=False
	):
		graph = cls(strict=strict)
		for index, start_name, end_name, edge_name in zip(range(len(start)), start, end, edge):
			start_node = graph.add_node(name=start_name, if_node_exists='ignore')
			end_node = graph.add_node(name=end_name, if_node_exists='ignore')
			graph.connect(start=start_node, end=end_node, id=index, label=edge_name)
		return graph

	@staticmethod
	def get_object_descendants(obj, depth=None, _descendants=None):
		_descendants = [] or _descendants
		if depth is not None:
			if depth == 0:
				return []
		result = obj.__children__()


	@classmethod
	def from_object(cls, obj, strict=False, max_depth=None, max_height=None):
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

	def append(self, obj):
		try:
			dictionary = obj.__graph_dict__()
		except AttributeError:
			dictionary = obj

		if 'strict' in dictionary:
			self._is_strict = dictionary['strict']

		for node_name, node_dict in dictionary['nodes'].items():
			if 'style' in node_dict['meta_data']:
				style = NodeStyle(**node_dict['meta_data']['style'])
			else:
				style = None
			self.add_node(name=node_name, label=node_dict['label'], value=node_dict['value'], style=style)
		for parent, child in dictionary['edges']:
			self.connect(start=parent, end=child)
		return self

	@classmethod
	def from_dict(cls, obj):
		graph = cls()
		graph.append(obj=obj)
		return graph

