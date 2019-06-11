from ._BasicGraph import BasicGraph
from .graph_style.GraphStyle import GraphStyle, DEFAULT_BACKGROUND_COLOUR, DEFAULT_COLOUR_SCHEME

import graphviz
import os
from functools import wraps
import random


def draw_graph(
		obj, colour_scheme=None, strict=True, ordering=True, direction='LR',
		path=None, height=None, width=None
):
	graph = Graph(obj=obj, strict=strict, ordering=ordering)

	return graph.render(
		colour_scheme=colour_scheme, direction=direction,
		path=path, height=height, width=width
	)


class Graph(BasicGraph):
	def __init__(self, obj=None, strict=True, ordering=True):
		super().__init__(strict=strict, ordering=ordering)
		self._style = GraphStyle(graph=self)
		if obj:
			self.append(obj=obj)

	def __getstate__(self):
		state = super().__getstate__()
		state.update({'style': self._style})
		return state

	def __setstate__(self, state):
		super().__setstate__(state=state)
		self._style = state['style']
		self._nodes_have_graph = False
		self.update_nodes()

	@property
	def style(self):
		"""
		:rtype: GraphStyle
		"""
		return self._style

	def reset_styles(self):
		for node in self.nodes:
			node.style = None
			for edge in node.edges:
				edge.style = None

	@wraps(BasicGraph.connect)
	def connect(self, **kwargs):
		self.style.reset_node_colours()
		super().connect(**kwargs)

	def disconnect(self, edge):
		self.style.reset_node_colours()
		super().disconnect(edge=edge)

	def add_colour_scheme(self, name='default', colour_scheme=DEFAULT_COLOUR_SCHEME, background_colour=DEFAULT_BACKGROUND_COLOUR):
		self.style.add_colours(name=name, colour_scheme=colour_scheme, background_colour=background_colour)

	def get_graphviz_header(self, direction='LR', height=None, width=None):
		if self._is_strict:
			first_part = 'strict digraph G {\n'
		else:
			first_part = 'digraph G{\n'

		second_part = ''
		second_part += f'\tbgcolor="{self.style.background_colour.hexadecimal}";\n'

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

	def get_graphviz_str(self, direction='LR', height=None, width=None):
		nodes_str = '\t{\n\t\t' + '\n\t\t'.join([node.get_graphviz_str() for node in self.nodes_dict.values()]) + '\n\t}\n'
		edges_str = '\t' + '\n\t'.join([edge.get_graphviz_str() for edge in self.edges]) + '\n'
		header = self.get_graphviz_header(direction=direction, height=height, width=width)
		return header + nodes_str + edges_str + '}'

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
			self.style.node_styles.update(dictionary['node_styles'])

		if 'edge_styles' in dictionary:
			self.style.edge_styles.update(dictionary['edge_styles'])

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

	@classmethod
	def from_dict(cls, obj):
		graph = cls()
		graph.append(obj=obj)
		return graph

	def __graph__(self):
		nodes_dict = {}
		edges_list = []
		for node in self.nodes:
			nodes_dict[node.id] = {
				'label': node.raw_label,
				'value': node.value,
				'style': node.style
			}

			for edge in node.outward_edges:
				edges_list.append([
					edge.start.id,
					edge.end.id,
					{
						'id': edge.raw_id,
						'label': edge.raw_label,
						'value': edge.value,
						'style': edge.style
					}
				])

		return {
			'strict': self._is_strict,
			'ordering': self._ordering,
			'node_styles': self.style.node_styles,
			'edge_styles': self.style.edge_styles,
			'nodes': nodes_dict,
			'edges': edges_list
		}

	def is_similar_to(self, other):
		"""
		:type other: Graph
		:rtype: bool
		"""
		if super().is_similar_to(other=other):
			return False

		if self.style != other.style:
			return False

		return True

	def render(
			self, path=None, view=True, direction='LR', height=None, width=None,
			colour_scheme=None
	):
		self.add_colour_scheme(name='default', colour_scheme=colour_scheme)

		if path is None:
			return graphviz.Source(source=self.get_graphviz_str(direction=direction))
		else:
			filename, file_extension = os.path.splitext(path)
			output_format = file_extension.lstrip('.')
			graphviz_str = self.get_graphviz_str(direction=direction, height=height, width=width)
			source = graphviz.Source(source=graphviz_str, format=output_format)
			return source.render(filename=filename, view=view)

	draw = render
	display = render
	visualize = render

	@classmethod
	def random(
			cls, num_nodes, cycle=False, start_index=1, connection_probability=0.5,
			ordering=True,
	):
		"""
		:param int num_nodes:
		:param bool cycle:
		:param int start_index:
		:param float connection_probability:
		:param bool ordering:
		:rtype: BasicGraph
		"""
		graph = cls(strict=True, ordering=ordering)
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
