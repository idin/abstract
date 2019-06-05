from ._BasicGraph import BasicGraph
from .Style import NodeStyle, EdgeStyle

from colouration import Scheme
import graphviz
import os
from functools import wraps

DEFAULT_COLOUR_SCHEME = 'pastel19'


def draw_graph(
		obj, colour_scheme=None, strict=True, ordering=True, background_colour=None, direction='LR',
		path=None, height=None, width=None
):
	graph = Graph(obj=obj, strict=strict, ordering=ordering)

	return graph.render(
		colour_scheme=colour_scheme, background_colour=background_colour, direction=direction,
		path=path, height=height, width=width
	)


class Graph(BasicGraph):
	def __init__(self, obj=None, strict=True, ordering=True):
		super().__init__(strict=strict, ordering=ordering)
		self._node_colour_indices = None
		self._colour_scheme = None
		self._node_styles = {}
		self._edge_styles = {}
		self._node_styles_counter = 0
		self._edge_styles_counter = 0
		if obj:
			self.append(obj=obj)

	def __getstate__(self):
		state = super().__getstate__()
		state.update({
			'node_styles': self._node_styles,
			'edge_styles': self._edge_styles,
			'node_styles_counter': self._node_styles_counter,
			'edge_styles_counter': self._edge_styles_counter,
			'node_colour_indices': self._node_colour_indices
		})
		return state

	def __setstate__(self, state):
		super().__setstate__(state=state)
		self._node_styles = state['node_styles']
		self._edge_styles = state['edge_styles']
		self._node_styles_counter = state['node_styles_counter']
		self._edge_styles_counter = state['edge_styles_counter']
		self._node_colour_indices = state['node_colour_indices']
		self._nodes_have_graph = False
		self.update_nodes()

	@wraps(BasicGraph.connect)
	def connect(self, **kwargs):
		self._node_colour_indices = None
		super().connect(**kwargs)

	def disconnect(self, edge):
		self._node_colour_indices = None
		super().disconnect(edge=edge)

	def add_colour_scheme(self, name='default', colour_scheme=None):
		colour_scheme = Scheme.auto(obj=colour_scheme or DEFAULT_COLOUR_SCHEME)
		self._node_styles[name] = [
			NodeStyle(
				name=colour.name,
				text_colour=colour.farthest_gray.hexadecimal,
				fill_colour=colour.hexadecimal,
				colour=colour.darken().get_hexadecimal(opacity=0.8)
			)
			for colour in colour_scheme.colours
		]
		self._edge_styles[name] = [
			EdgeStyle(
				name=colour.name,
				colour=colour.darken().get_hexadecimal(opacity=0.5)
			)
			for colour in colour_scheme.colours
		]

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
		header = self.get_graphviz_header(
			direction=direction, height=height, width=width, background_colour=background_colour
		)
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
		if super().is_similar_to(other=other):
			return False

		if self._node_styles != other._node_styles:
			return False

		if self._edge_styles != other._edge_styles:
			return False

		return True

	def render(
			self, path=None, view=True, direction='LR', height=None, width=None, background_colour=None,
			colour_scheme=None
	):
		self.add_colour_scheme(name='default', colour_scheme=colour_scheme)

		if path is None:
			return graphviz.Source(
				source=self.get_graphviz_str(direction=direction, background_colour=background_colour)
			)
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
