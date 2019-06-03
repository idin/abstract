from .Node import Node
from .Edge import Edge
from .Style import NodeStyle, EdgeStyle
from .get_ancestors import get_ancestors
from .get_descendants import get_descendants
from .parse_indentations_function import parse_indentations
from .Palette import Palette

import graphviz
import warnings
import os
from copy import deepcopy
import random


def draw_graph(*args, **kwargs):
	return Graph(*args, **kwargs).render()


class Graph:
	def __init__(self, obj=None, strict=True, ordering=True, palette=None):
		self._nodes_dict = {}
		self._is_strict = strict
		self._ordering = ordering
		self._node_colour_indices = None

		if palette is None:
			self._palette = Palette(
				hue=[0, 1], saturation=[0.66, 0.66], luminosity=[0.5, 0.5], num_levels=6
			)

		else:
			self._palette = palette

		self._node_styles = {
			'default': [
				NodeStyle(
					name=self._palette.get_hex(index=index),
					text_colour=self._palette.get_hex(index=index, l=0.2, s=0.7),
					fill_colour=self._palette.get_hex(index=index, l=0.98, s=0.1),
					colour=self._palette.get_hex(index=index, l=0.5, s=0.35) + '66'
				)
				for index in range(self._palette.num_levels)
			],
			'dark': [
				NodeStyle(
					name=self._palette.get_hex(index=index),
					text_colour=self._palette.get_hex(index=index, l=1),
					fill_colour=self._palette.get_hex(index=index, l=0.4, s=0.2),
					colour=self._palette.get_hex(index=index, l=0.5) + '66'
				)
				for index in range(self._palette.num_levels)
			]
		}
		self._edge_styles = {
			'default': [
				EdgeStyle(
					name=self._palette.get_hex(index=index),
					colour=self._palette.get_hex(index=index, l=0.5, s=0.35) + '66'
				)
				for index in range(self._palette.num_levels)
			]
		}


		self._node_counter = 0
		self._node_styles_counter = 0
		self._edge_styles_counter = 0
		self._nodes_have_graph = True
		# if a dictionary or an object with a __graph__() method is passed use that to create the graph
		if obj:
			self.append(obj=obj)

	def copy(self):
		return deepcopy(self)

	def filter(self, nodes=None, direction='to_and_from', filter_type='include'):
		"""
		:param list[str] or list[Node] nodes:
		:param str direction:
		:rtype Graph
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

	def get_node_style(self, style_name, number=None, node_name=None):
		styles = self._node_styles[style_name]
		if isinstance(styles, NodeStyle):
			return styles
		else:
			if number is None:
				number = self.node_colour_indices[node_name]
			return styles[number % len(styles)]

	def get_edge_style(self, style_name, number=None, node_name=None):
		styles = self._edge_styles[style_name]
		if isinstance(styles, EdgeStyle):
			return styles
		else:
			if number is None:
				number = self.node_colour_indices[node_name]
			return styles[number % len(styles)]

	def __getstate__(self):
		return {
			'nodes_dict': self.nodes_dict,
			'is_strict': self._is_strict,
			'ordering': self._ordering,
			'node_styles': self._node_styles,
			'edge_styles': self._edge_styles,
			'node_counter': self._node_counter,
			'node_styles_counter': self._node_styles_counter,
			'edge_styles_counter': self._edge_styles_counter,
			'node_colour_indices': self._node_colour_indices
		}

	def __setstate__(self, state):
		self._nodes_dict = state['nodes_dict']
		self._is_strict = state['is_strict']
		self._ordering = state['ordering']
		self._node_styles = state['node_styles']
		self._edge_styles = state['edge_styles']
		self._nodes_have_graph = False
		self._node_counter = state['node_counter']
		self._node_styles_counter= state['node_styles_counter']
		self._edge_styles_counter = state['edge_styles_counter']
		self._node_colour_indices = state['node_colour_indices']
		self.update_nodes()

	def __contains__(self, item):
		return item in self._nodes_dict

	def update_nodes(self):
		if not self._nodes_have_graph:
			for node in self._nodes_dict.values():
				node._graph = self
				node.update_edges()
		self._nodes_have_graph = True

	@property
	def nodes_dict(self):
		"""
		:rtype: dict[str, Node]
		"""
		return self._nodes_dict

	@property
	def nodes(self):
		"""
		:rtype: list[Node]
		"""
		return list(self.nodes_dict.values())

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

	def get_graphviz_header(self, direction='LR', height=None, width=None, background_colour=None):
		if self._is_strict:
			first_part = 'strict digraph G {\n'
		else:
			first_part = 'digraph G{\n'

		second_part = ''
		if background_colour is not None:
			second_part += f'\tbgcolor="{background_colour}";\n'

		if not self._ordering:
			second_part += '\tordering=out;\n'

		if height is not None and width is not None:
			second_part += f'\tsize="{width},{height}!";\n'
			second_part += '\tratio="fill";\n'
		elif height is not None:
			second_part += f'\tsize="{height}!";\n'
			second_part += '\tratio="fill";\n'
		elif width is not None:
			second_part += f'\tsize="{width}!";\n'
			second_part += '\tratio="fill";\n'

		direction = direction.upper()
		if direction != 'TB':
			third_part = f'\trankdir="{direction}"'
		else:
			third_part = ''

		return first_part + second_part + third_part

	def get_graphviz_str(self, direction='LR', height=None, width=None, background_colour=None):
		nodes_str = '\t{\n\t\t' + '\n\t\t'.join([node.get_graphviz_str() for node in self.nodes_dict.values()]) + '\n\t}\n'
		edges_str = '\t' + '\n\t'.join([edge.get_graphviz_str() for edge in self.edges]) + '\n'
		header = self.get_graphviz_header(direction=direction, height=height, width=width, background_colour=background_colour)
		return header + nodes_str + edges_str + '}'

	def render(self, path=None, view=True, direction='LR', height=None, width=None, background_colour=None):

		if path is None:
			return graphviz.Source(source=self.get_graphviz_str(direction=direction))
		else:
			filename, file_extension = os.path.splitext(path)
			output_format = file_extension.lstrip('.')
			graphviz_str = self.get_graphviz_str(
				direction=direction, height=height, width=width, background_colour=background_colour
			)
			source = graphviz.Source(source=graphviz_str, format=output_format)
			return source.render(filename=filename, view=view)

	draw = render
	display = render
	visualize = render

	def get_node(self, node):
		"""
		:type node: Node or str
		:rtype: Node
		"""
		if isinstance(node, str):
			return self.nodes_dict[node]
		else:
			return self.nodes_dict[node.id]

	def get_node_name(self, node):
		"""
		:type node: Node or str
		:rtype: Node
		"""
		if isinstance(node, str):
			return self.nodes_dict[node].id
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
		ancestors, ancestors_dict = self._get_ancestors(node=node, nodes_travelled=None)
		if distance:
			return ancestors_dict
		else:
			return ancestors

	def is_node_in_loop(self, node):
		node = self.get_node(node)
		return node in self.get_ancestors(node=node, distance=False)

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
		:param NodeStyle or str style: style of the node
		:param str if_node_exists: what to do if a node with that name exists. One of 'warn', 'error', 'ignore'
		:param kwargs:
		:rtype: Node
		"""

		if name in self.nodes_dict:

			if if_node_exists == 'ignore':
				pass
			elif if_node_exists == 'warn':
				warnings.warn(f'Warning! A node with name "{id}" already exists in graph!')
			else:
				raise KeyError(f'duplicate node id:"{id}"!')

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
				style=style, index=self.get_node_index(), **kwargs
			)
			self.nodes_dict[name] = node
			return node

	def get_node_index(self):
		index = self._node_counter
		self._node_counter += 1
		return index

	def connect(self, start, end, id=None, label=None, value=None, style=None, if_edge_exists='warn', **kwargs):
		"""
		:param Node or str start: starting node
		:param Node or str end: end node
		:param id:
		:param str label: optional label of the edge
		:param value:
		:param EdgeStyle or NoneType style:
		:param if_edge_exists:
		:param kwargs:
		:return:
		"""
		start = self.get_node(node=start)
		end = self.get_node(node=end)
		edge_id = (start.id, end.id, id)

		# reset node colour indices:
		self._node_colour_indices = None

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
		del self.nodes_dict[node.id]

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
		return result

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
			dictionary = obj.__graph__()
		except AttributeError:
			dictionary = obj

		if 'strict' in dictionary:
			self._is_strict = dictionary['strict']

		if 'ordering' in dictionary:
			self._ordering = dictionary['ordering']

		if 'node_styles' in dictionary:
			self._node_styles.update(dictionary['node_styles'])

		if 'edge_styles' in dictionary:
			self._edge_styles.update(dictionary['edge_styles'])

		for node_name, node_dict in dictionary['nodes'].items():
			self.add_node(name=node_name, **node_dict)

		for parent_child_edge_dict in dictionary['edges']:

			if len(parent_child_edge_dict) == 2:
				parent, child = parent_child_edge_dict
				self.connect(start=parent, end=child)

			elif len(parent_child_edge_dict) == 3:
				parent, child, edge_dict = parent_child_edge_dict
				self.connect(start=parent, end=child, **edge_dict)

			elif len(parent_child_edge_dict) < 2:
				raise ValueError('Too few objects in an edge definition!')
			else:
				raise ValueError('Too many objects in an edge definition!')

		return self

	def __graph__(self):
		nodes_dict = {}
		edges_list = []
		for node in self.nodes:
			nodes_dict[node._id] = {
				'label': node._label,
				'value': node._value,
				'style': node._style
			}

			for edge in node.outward_edges:
				edges_list.append([
					edge.start._id,
					edge.end._id,
					{
						'id': edge._id,
						'label': edge._label,
						'value': edge._value,
						'style': edge._style
					}
				])

		return {
			'strict': self._is_strict,
			'ordering': self._ordering,
			'node_styles': self._node_styles,
			'edge_styles': self._edge_styles,
			'nodes': nodes_dict,
			'edges': edges_list
		}

	def is_similar_to(self, other):
		"""
		:type other: Graph
		:rtype: bool
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

		if self._node_styles != other._node_styles:
			return False

		if self._edge_styles != other._edge_styles:
			return False

		return True

	@classmethod
	def from_dict(cls, obj):
		graph = cls()
		graph.append(obj=obj)
		return graph

	@classmethod
	def from_indented_text(cls, root, lines, indent=None):
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

	@property
	def node_colour_indices(self):
		if self._node_colour_indices is None:
			sorted_nodes = [name for name, _ in sorted(self.nodes_dict.items(), key=lambda name_node: (-name_node[1].num_outward_edges, name_node[1].index))]
			self._node_colour_indices = {name: index for index, name in enumerate(sorted_nodes)}
		return self._node_colour_indices

	@classmethod
	def random(cls, num_nodes, cycle=False, start_index=1, connection_probability=0.5, ordering=True, palette=None):
		"""
		:param int num_nodes:
		:param bool cycle:
		:param float connection_probability:
		:param bool ordering:
		:param palette:
		:rtype: Graph
		"""
		graph = cls(strict=True, ordering=ordering, palette=palette)
		connection_probability = min(1.0, max(0.0, connection_probability))
		node_names = [i + start_index for i in range(num_nodes)]
		for n in node_names:
			graph.add_node(name=str(n))

		for n1 in node_names:
			for n2 in node_names:
				if random.uniform(0, 1) < connection_probability:
					if cycle:
						graph.connect(start=str(n1), end=str(n2))
					elif n1 < n2:
						graph.connect(start=str(n1), end=str(n2))

		return graph

	def __add__(self, other):
		"""
		:type other: Graph
		:rtype: Graph
		"""
		return self.add(other=other)

	def add(self, other, add_values_function=None):
		"""
		:type self: Graph
		:type other: Graph
		:type add_values_function: callable
		:rtype: Graph
		"""

		d1 = self.__graph__()
		d2 = other.__graph__()

		node_styles = d1['node_styles']
		node_styles.update(d2['node_styles'])

		edge_styles = d1['edge_styles']
		edge_styles.update(d2['edge_styles'])

		if add_values_function is None:
			def add_values_function(x, y):
				if x is None or y is None:
					return x or y
				else:
					return x + y

		nodes = {}
		for id in set(d1['nodes'].keys()).union(d2['nodes'].keys()):
			if id in d1['nodes'] and id in d2['nodes']:
				node1 = d1['nodes'][id]
				node2 = d2['nodes'][id]
				n = {}
				for key in set(node1.keys()).union(node2.keys()):
					if key in node1 and key in node2:
						if key == 'value':
							n[key] = add_values_function(node2[key], node2[key])
						else:
							n[key] = node1[key] or node2[key]
					elif key in node1:
						n[key] = node1[key]
					else:
						n[key] = node2[key]
				nodes[id] = n
			elif id in d1['nodes']:
				nodes[id] = d1['nodes'][id]
			else:
				nodes[id] = d2['nodes'][id]

		edges = {}
		for edge2 in d1['edges'] + d2['edges']:
			start2, end2, edge2_dict = edge2
			id2 = edge2_dict['id']
			if (start2, end2, id2) in edges:
				edge1 = edges[(start2, end2, id2)]
				edge1_dict = edge1[2]
				for key in set(edge1_dict.keys()).union(set(edge2_dict.keys())):
					if key in edge1_dict and key in edge2_dict:
						if key == 'value':
							edge1_dict[key] = add_values_function(edge1_dict[key], edge2_dict[key])
						else:
							edge1_dict[key] = edge1_dict[key] or edge2_dict[key]
					elif key in edge2_dict:
						edge1_dict[key] = edge2_dict[key]
			else:
				edges[(start2, end2, id2)] = start2, end2, edge2_dict
		edges = edges.values()

		result_representation = {
			'strict': d1['strict'],
			'ordering': d1['ordering'],
			'node_styles': node_styles,
			'edge_styles': edge_styles,
			'nodes': nodes,
			'edges': edges
		}
		result = self.__class__(obj=result_representation)

		return result

