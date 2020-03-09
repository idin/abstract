from ._BasicGraph import BasicGraph
from .graph_style.NodeStyle import NodeStyle
from .graph_style.EdgeStyle import EdgeStyle
from .graph_style.RootAndBranchStylist import RootAndBranchStylist
import graphviz
import os
from functools import wraps
import random
from colouration import Colour

DEFAULT_BACKGROUND_COLOUR_NAME = '#FAFAFA'


def draw_graph(
		obj, strict=True, ordering=True, direction='LR',
		path=None, height=None, width=None, pad=None
):
	graph = Graph(obj=obj, strict=strict, ordering=ordering, direction=direction)

	return graph.render(
		path=path, height=height, width=width, pad=pad
	)


class Graph(BasicGraph):
	def __init__(
			self, obj=None, strict=True, ordering=True, node_style=None, edge_style=None,
			colour_scheme=None, background_colour=DEFAULT_BACKGROUND_COLOUR_NAME,
			font='helvetica', node_shape=None, node_shape_style=None,
			direction='LR', stylist=None, label='\nPowered by Abstract', label_url='https://pypi.org/project/abstract/',
			label_location='bottom', font_size=10, label_colour='deepskyblue3', label_background_colour=None,
			**kwargs
	):

		self._background_colour = None
		self._direction = direction
		self.background_colour = background_colour

		self._graph_node_style_overwrite = None
		self._graph_edge_style_overwrite = None
		self._node_style_overwrites = {}
		self._edge_style_overwrites = {}
		self._node_colour_overwrites = {}
		self._edge_colour_overwrites = {}
		self._label = label
		self._label_location = label_location
		self._label_colour = label_colour
		self._label_url = label_url
		self._label_background_colour = label_background_colour

		self._font = font
		self._font_size = font_size
		self._kwargs = kwargs

		if isinstance(obj, self.__class__):
			colour_scheme_2 = obj._colour_scheme
		else:
			try:
				obj = obj.__graph__()
			except AttributeError:
				pass

			if isinstance(obj, dict) and 'colour_scheme' in obj:
				colour_scheme_2 = obj['colour_scheme']
			else:
				colour_scheme_2 = None

		colour_scheme = colour_scheme or colour_scheme_2

		self._colour_scheme = colour_scheme

		if stylist is None:
			stylist = RootAndBranchStylist(
				colour_scheme=colour_scheme, node_style=node_style, font=font, node_shape=node_shape,
				node_shape_style=node_shape_style, edge_style=edge_style
			)

		self._stylist = stylist

		super().__init__(strict=strict, ordering=ordering)

		if obj:
			self.append(obj=obj)

	def __getstate__(self):
		state = super().__getstate__()
		return state

	def update_nodes(self):
		if not self._nodes_have_graph:
			for node in self._nodes_dict.values():
				node._graph = self
				node.update_edges()
		self._nodes_have_graph = True

	def __setstate__(self, state):
		super().__setstate__(state=state)
		'''
		self._node_style = state['node_style']
		self._edge_style = state['edge_style']
		'''
		self._nodes_have_graph = False
		self.update_nodes()

	@wraps(BasicGraph.connect)
	def connect(self, start, end, style=None, **kwargs):
		return super().connect(start=start, end=end, style=style, **kwargs)

	@wraps(BasicGraph.add_node)
	def add_node(self, name, style=None, **kwargs):
		return super().add_node(name=name, style=style, **kwargs)

	@wraps(BasicGraph.disconnect)
	def disconnect(self, edge):
		return super().disconnect(edge=edge)

	@property
	def background_colour(self):
		"""
		:rtype: Colour
		"""
		return self._background_colour

	@background_colour.setter
	def background_colour(self, background_colour):
		"""
		:type background_colour: Colour or str
		"""
		if not isinstance(background_colour, Colour):
			background_colour = Colour(obj=background_colour)
		self._background_colour = background_colour

	@property
	def node_styles(self):
		"""
		:rtype: dict[str, NodeStyle]
		"""
		return {name: node.style for name, node in self.nodes_dict.items() if node.has_style()}

	@property
	def edge_styles(self):
		"""
		:rtype: dict[str, EdgeStyle]
		"""
		return {edge.id: edge.style for node in self.nodes for edge in node.outward_edges if edge.has_style()}

	def stylize(self):
		if self._graph_node_style_overwrite is not None:
			for node in self.nodes:
				node.style = self._graph_node_style_overwrite

		if self._graph_edge_style_overwrite is not None:
			for edge in self.edges:
				edge.style = self._graph_edge_style_overwrite

		self._stylist.paint(graph=self)

		for name, style in self._node_style_overwrites.items():
			self.nodes_dict[name].style = style

		for edge_id, style in self._edge_style_overwrites.items():
			self.edges_dict[edge_id].style = style

		for name, colour in self._node_colour_overwrites.items():
			node = self.nodes_dict[name]
			style = node.style.copy()
			style.reset_colours()
			style.colour = colour
			node.style = style

		for edge_id, colour in self._edge_colour_overwrites.items():
			edge = self.edges_dict[edge_id]
			_ = edge.style.colour
			style = edge.style.copy()
			style.reset_colours()
			style.colour = colour
			edge.style = style
			_ = edge.style.colour

		if self._graph_node_style_overwrite is not None:
			for node in self.nodes:
				node.style.complement(self._graph_node_style_overwrite)

		if self._graph_edge_style_overwrite is not None:
			for edge in self.edges:
				edge.style.complement(self._graph_edge_style_overwrite)

	def get_graphviz_header(self, dpi=300, direction=None, height=None, width=None, pad=None):
		"""
		:type direction: str or NoneType
		:type dpi: int
		:type height: float or int or NoneType
		:type width: float or int or NoneType
		:type pad: int or float or NoneType
		:rtype: str
		"""
		direction = direction or self._direction

		if self._is_strict:
			first_part = 'strict digraph G {\n'
		else:
			first_part = 'digraph G{\n'

		second_part = ''

		attributes = {}
		if self._label is not None:
			if self._label.startswith('<') and self._label.endswith('>'):
				attributes['label'] = f'{self._label}'
			else:
				if self._label_background_colour is not None:
					html = f'<table border="0" cellborder="0"><tr><td bgcolor="{self._label_background_colour}" title="{self._label}">{self._label} </td></tr></table>'
					if self._label_location[0] == 't':
						attributes['label'] = f'<{html}\n>'
					else:
						attributes['label'] = f'<\n{html}>'
				else:
					attributes['label'] = f'"{self._label}"'

			if self._label_location is not None:
				attributes['labelloc'] = f'"{self._label_location[0]}"'
			if self._font_size is not None:
				attributes['fontsize'] = f'{self._font_size}'
			if self._font is not None:
				attributes['fontname'] = f'"{self._font}"'
			if self._label_colour is not None:
				attributes['fontcolor'] = f'"{self._label_colour}"'
			if self._label_url is not None:
				attributes['href'] = f'"{self._label_url}"'
				attributes['target'] = '"_blank"'
		if dpi is not None:
			attributes['dpi'] = f'{dpi}'
		for key, value in self._kwargs.items():
			if isinstance(value, int):
				attributes[key] = value
			else:
				attributes[key] = f'"{value}"'

		if len(attributes) > 0:
			second_part += '\tGraph [' + ', '.join([f'{key} = {value}' for key, value in attributes.items()]) + ' ];\n'

		second_part += f'\tbgcolor="{self.background_colour.hexadecimal}";\n'

		if pad is not None:
			second_part += f'\tpad="{pad}";\n'

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

	def get_graphviz_str(self, direction=None, dpi=300, height=None, width=None, pad=None):
		"""
		:type direction: str or NoneType
		:type dpi: int
		:type height: float or int or NoneType
		:type width: float or int or NoneType
		:type pad: int or float or NoneType
		:rtype: str
		"""
		direction = direction or self._direction

		nodes_str = '\t{\n\t\t' + '\n\t\t'.join([node.get_graphviz_str() for node in self.nodes_dict.values()]) + '\n\t}\n'
		edges_str = '\t' + '\n\t'.join([edge.get_graphviz_str() for edge in self.edges]) + '\n'
		header = self.get_graphviz_header(direction=direction, dpi=dpi, height=height, width=width, pad=pad)
		return header + nodes_str + edges_str + '}'

	def append(self, obj):
		"""
		adds nodes and edges from an object's __graph__() method which is essentially just a dictionary
		:type obj: Object
		:rtype: Graph
		"""
		if isinstance(obj, (list, tuple)):
			for item in obj:
				self.append(obj=item)
			return self

		else:
			try:
				dictionary = obj.__graph__()
			except AttributeError:
				dictionary = obj

			if not isinstance(dictionary, dict):
				raise TypeError(f'{type(obj)} cannot be converted to a Graph. It needs to have a __graph__() method.')  # ToDo cite proper link for explanation

			if 'strict' in dictionary:
				self._is_strict = dictionary['strict']

			if 'ordering' in dictionary:
				self._ordering = dictionary['ordering']

			if 'graph_node_style' in dictionary:
				self._graph_node_style_overwrite = dictionary['graph_node_style']

			if 'graph_edge_style' in dictionary:
				self._graph_edge_style_overwrite = dictionary['graph_edge_style']

			if 'direction' in dictionary:
				self._direction = dictionary['direction']

			if isinstance(dictionary['nodes'], dict):
				for node_name, node_dict in dictionary['nodes'].items():
					self.add_node(name=node_name, **node_dict)
			else:
				for node_name in dictionary['nodes']:
					self.add_node(name=node_name)

			edges_dict = {}
			for parent_child_edge_dict in dictionary['edges']:

				if len(parent_child_edge_dict) == 2:
					parent, child = parent_child_edge_dict
					edge = self.connect(start=parent, end=child)
					edges_dict[(parent, child)] = edge.id

				elif len(parent_child_edge_dict) == 3:
					parent, child, edge_dict = parent_child_edge_dict
					edge = self.connect(start=parent, end=child, **edge_dict)
					edges_dict[(parent, child)] = edge.id

				elif len(parent_child_edge_dict) < 2:
					raise ValueError('Too few objects in an edge definition!')
				else:
					raise ValueError('Too many objects in an edge definition!')

			if 'node_styles' in dictionary:
				for name, node_style in dictionary['node_styles'].items():
					self._node_style_overwrites[name] = node_style

			if 'edge_styles' in dictionary:
				for parent_child_edge_id, edge_style in dictionary['edge_styles'].items():
					edge_id = edges_dict[parent_child_edge_id]
					self._edge_colour_overwrites[edge_id] = edge_style

			if 'node_colours' in dictionary:
				for name, colour in dictionary['node_colours'].items():
					self._node_colour_overwrites[name] = colour

			if 'edge_colours' in dictionary:
				for parent_child_edge_id, colour in dictionary['edge_colours'].items():
					edge_id = edges_dict[parent_child_edge_id]
					self._edge_colour_overwrites[edge_id] = colour

			return self

	@classmethod
	def from_dict(cls, obj):
		"""
		:param obj:
		:rtype: Graph
		"""
		graph = cls()
		graph.append(obj=obj)
		return graph

	def __graph__(self):
		"""
		:rtype: dict
		"""
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
			'node_styles': self._node_style_overwrites,
			'edge_styles': self._edge_style_overwrites,
			'graph_node_style': self._graph_node_style_overwrite,
			'graph_edge_style': self._graph_edge_style_overwrite,
			'node_colours': self._node_colour_overwrites,
			'nodes': nodes_dict,
			'edges': edges_list
		}

	@classmethod
	def random(
			cls, num_nodes, cycle=False, start_index=1, connection_probability=0.5,
			ordering=True, seed=None
	):
		"""
		creates a random graph
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

		if seed is not None:
			random.seed(seed)
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
		combines two graphs
		:type other: Graph
		:rtype: Graph
		"""
		return self.add(other=other)

	def add(self, other, add_values_function=None):
		"""
		combines two graphs
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
		for the_id in set(d1['nodes'].keys()).union(d2['nodes'].keys()):
			if the_id in d1['nodes'] and the_id in d2['nodes']:
				node1 = d1['nodes'][the_id]
				node2 = d2['nodes'][the_id]
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
				nodes[the_id] = n
			elif the_id in d1['nodes']:
				nodes[the_id] = d1['nodes'][the_id]
			else:
				nodes[the_id] = d2['nodes'][the_id]

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

	def render(
			self, path=None, view=True, direction=None, height=None, width=None, dpi=300, pad=None
	):
		direction = direction or self._direction

		self.stylize()

		if path is None:
			return graphviz.Source(source=self.get_graphviz_str(direction=direction, pad=pad, dpi=None))
		else:
			filename, file_extension = os.path.splitext(path)
			output_format = file_extension.lstrip('.')
			graphviz_str_to_save = self.get_graphviz_str(direction=direction, height=height, width=width, pad=pad, dpi=dpi)
			to_save = graphviz.Source(source=graphviz_str_to_save, format=output_format)
			to_save.render(filename=filename, view=view)
			graphviz_str_to_display = graphviz.Source(
				source=self.get_graphviz_str(direction=direction, pad=pad, dpi=None)
			)
			return graphviz_str_to_display

	def display(self, p=None, pad=0.2, direction=None, path=None, height=None, width=None, dpi=300):
		try:
			from IPython.core.display import display
			display(self.render(
				pad=pad, dpi=dpi, direction=direction or self._direction, path=path, height=height, width=width
			))
		except ImportError:
			if p is not None:
				p.pretty(self.get_tree_str())
			else:
				print(self.get_tree_str())

	draw = display
	visualize = display

	def _repr_pretty_(self, p, cycle):
		if cycle:
			p.text('Graph')
		else:
			self.display(p=p)
