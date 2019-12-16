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
			font=None, node_shape=None, node_shape_style=None,
			direction='LR', stylist=None
	):
		self._colour_scheme = None
		self._background_colour = None
		self._direction = direction
		self.colour_scheme = colour_scheme
		self.background_colour = background_colour

		self._graph_node_style_overwrite = None
		self._graph_edge_style_overwrite = None
		self._node_style_overwrites = {}
		self._edge_style_overwrites = {}
		self._node_colour_overwrites = {}

		if stylist is None:
			stylist = RootAndBranchStylist(
				colour_scheme=colour_scheme, node_style=node_style, font=font, node_shape=node_shape,
				node_shape_style=node_shape_style, edge_style=edge_style
			)

		self._stylist = stylist

		super().__init__(strict=strict, ordering=ordering)

		'''
		self._node_style = node_style or (
			lambda node: mix_node_style_of_parents(node=node, font=font, shape=node_shape, shape_style=node_shape_style)
		)
		self._edge_style = edge_style or (
			lambda edge: inherit_edge_style_from_start(edge=edge, font=font)
		)
		'''

		if obj:
			self.append(obj=obj)

	def __getstate__(self):
		state = super().__getstate__()
		state.update('_colou')
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
		super().connect(start=start, end=end, style=style, **kwargs)

	@wraps(BasicGraph.add_node)
	def add_node(self, name, style=None, **kwargs):
		super().add_node(name=name, style=style, **kwargs)

	@wraps(BasicGraph.disconnect)
	def disconnect(self, edge):
		super().disconnect(edge=edge)

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

	def get_graphviz_header(self, dpi=300, direction=None, height=None, width=None, pad=None):
		"""
		:type direction: str or NoneType
		:type height: float or int
		:type width: float or int
		:rtype: str
		"""
		direction = direction or self._direction

		if self._is_strict:
			first_part = 'strict digraph G {\n'
		else:
			first_part = 'digraph G{\n'

		second_part = ''
		if dpi is not None:
			second_part += f'\tGraph [ dpi = {dpi} ];\n'

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
		:type height: float or int
		:type width: float or int
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
		try:
			dictionary = obj.__graph__()
		except AttributeError:
			dictionary = obj

		if 'strict' in dictionary:
			self._is_strict = dictionary['strict']

		if 'ordering' in dictionary:
			self._ordering = dictionary['ordering']

		if 'graph_node_style' in dictionary:
			self._graph_node_style_overwrite = dictionary['graph_node_style']

		if 'graph_edge_style' in dictionary:
			self._graph_edge_style_overwrite = dictionary['graph_edge_style']

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

		if 'node_styles' in dictionary:
			for name, node_style in dictionary['node_styles'].items():
				if node_style is not None:
					self._node_style_overwrites[name] = node_style

		edges_dict = self.edges_dict
		if 'edge_styles' in dictionary:
			for edge_id, edge_style in dictionary['edge_styles'].items():
				if edge_style is not None:
					self._edge_style_overwrites[edge_id] = edge_style

		if 'node_colours' in dictionary:
			for name, colour in dictionary['node_colours'].items():
				self._node_colour_overwrites[name] = colour

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
			ordering=True,
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
			graphviz_str_to_save = self.get_graphviz_str(direction=direction, height=height, width=width, pad=pad)
			to_save = graphviz.Source(source=graphviz_str_to_save, format=output_format)
			to_save.render(filename=filename, view=view)
			graphviz_str_to_display = graphviz.Source(source=self.get_graphviz_str(direction=direction, pad=pad, dpi=None))
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
