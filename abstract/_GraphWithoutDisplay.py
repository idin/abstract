from ._BasicGraph import BasicGraph
from .styling.NodeStyle import NodeStyle
from .styling.EdgeStyle import EdgeStyle
from graphviz import Source
import os
from functools import wraps
import random
from colouration import Colour
from .styling import stylize_with_pensieve, stylize_randomly
from typing import Optional, Union, Dict, Callable
from .Node import Node
from .Edge import Edge

DEFAULT_BACKGROUND_COLOUR_NAME = '#FAFAFA'
DEFAULT_PAD = 0.1


class GraphWithoutDisplay(BasicGraph):
	def __init__(
			self, obj=None, strict=False, ordering=True, node_style=None, edge_style=None,
			node_label_converter=None, edge_label_converter=None,
			colour_scheme='pensieve2', background_colour=DEFAULT_BACKGROUND_COLOUR_NAME,
			font='helvetica',
			direction='LR', stylist='pensieve', label='\nPowered by Abstract', label_url='https://github.com/idin/abstract',
			tooltip=None,
			label_location='bottom', font_size=10, label_colour='deepskyblue3', label_background_colour=None,
			style_overwrite_allowed=False,
			**kwargs
	):
		"""
		Initializes a GraphWithoutDisplay instance.

		Args:
			obj: The object to create the graph from.
			strict (bool): If True, the graph will be strict. Strict graphs have no multiple edges between the same nodes.
			ordering (bool): If True, the graph will maintain ordering.
			node_style (Optional[NodeStyle]): Global node style.
			edge_style (Optional[EdgeStyle]): Global edge style.
			node_label_converter (Optional[callable]): Function to convert node labels.
			edge_label_converter (Optional[callable]): Function to convert edge labels.
			colour_scheme (str): Colour scheme for the graph.
			background_colour (str): Background colour of the graph.
			font (str): Font for the graph.
			direction (str): Direction of the graph layout.
			stylist (str): Stylist for the graph.
			label (str): Label for the graph.
			label_url (str): URL for the label.
			tooltip (Optional[str]): Tooltip for the graph.
			label_location (str): Location of the label.
			font_size (int): Font size for the label.
			label_colour (str): Colour of the label.
			label_background_colour (Optional[str]): Background colour for the label.
			style_overwrite_allowed (bool): If False, a node style cannot be overwritten.
			**kwargs: Additional keyword arguments.
		"""

		self._background_colour = None
		self._direction = direction
		self.background_colour = background_colour

		self._global_node_style_overwrite = node_style
		self._global_edge_style_overwrite = edge_style
		self._node_style_overwrites = {}
		self._edge_style_overwrites = {}
		self._node_colour_overwrites = {}
		self._edge_colour_overwrites = {}
		self._label = label
		self._label_location = label_location
		self._label_colour = label_colour
		self._label_url = label_url
		self._label_background_colour = label_background_colour

		self._tooltip = tooltip

		self._font = font
		self._font_size = font_size
		self._kwargs = kwargs

		if isinstance(obj, self.__class__):
			colour_scheme = colour_scheme or obj._colour_scheme
		else:
			try:
				obj = obj.__graph__()
			except AttributeError:
				pass

		if isinstance(obj, dict):
			if 'colour_scheme' in obj:
				colour_scheme = colour_scheme or obj['colour_scheme']

			if 'style_overwrite_allowed' in obj:
				style_overwrite_allowed = obj['style_overwrite_allowed']

			if 'stylist' in obj:
				stylist = stylist or obj['stylist']
			if stylist is None:
				stylist = 'pensieve'

		self._colour_scheme = colour_scheme
		self._stylist = stylist
		self._style_overwrite_allowed = style_overwrite_allowed

		super().__init__(
			strict=strict, ordering=ordering,
			node_label_converter=node_label_converter, edge_label_converter=edge_label_converter
		)

		if obj:
			self.append(obj=obj)

	def __getstate__(self) -> Dict:
		"""
		Returns the state of the graph for pickling.
		Returns:
			Dict: The state of the graph.
		"""
		state = super().__getstate__()
		return state

	def update_nodes(self):
		"""Updates the nodes in the graph."""
		if not self._nodes_have_graph:
			for node in self._nodes_dict.values():
				node._graph = self
				node.update_edges()
		self._nodes_have_graph = True

	def __setstate__(self, state):
		"""
		Restores the state of the graph from a pickled state.
		Args:
			state: The pickled state of the graph.
		"""
		super().__setstate__(state=state)
		'''
		self._node_style = state['node_style']
		self._edge_style = state['edge_style']
		'''
		self._nodes_have_graph = False
		self.update_nodes()

	@wraps(BasicGraph.connect)
	def connect(self, start: Union[str, Node], end: Union[str, Node], style: Optional[EdgeStyle] = None, **kwargs) -> Edge:
		"""
		Connects two nodes in the graph.

		Args:
			start (Union[str, Node]): The starting node.
			end (Union[str, Node]): The ending node.
			style (Optional[EdgeStyle]): The style of the edge.
			**kwargs: Additional keyword arguments.

		Returns:
			Edge: The created edge.
		"""
		return super().connect(start=start, end=end, style=style, **kwargs)

	@wraps(BasicGraph.add_node)
	def add_node(self, name: str, style: Optional[NodeStyle] = None, **kwargs) -> Node:
		"""
		Adds a node to the graph.

		Args:
			name (str): The name of the new node.
			style (Optional[NodeStyle]): The style of the node.
			**kwargs: Additional keyword arguments.

		Returns:
			Node: The created node.
		"""
		# if name is a Node it should be handled by the BasicGraph.add_node method
		return super().add_node(name=name, style=style, **kwargs)

	@wraps(BasicGraph.disconnect)
	def disconnect(self, edge: Edge):
		"""
		Disconnects an edge from the graph.

		Args:
			edge (Edge): The edge to disconnect.
		"""
		return super().disconnect(edge=edge)

	@property
	def background_colour(self) -> Colour:
		"""
		Gets the background colour of the graph.
		
		Returns:
			Colour: The background colour of the graph.
		"""
		return self._background_colour

	@background_colour.setter
	def background_colour(self, background_colour: Union[Colour, str]):
		"""
		Sets the background colour of the graph.

		Args:
			background_colour (Union[Colour, str]): The background colour to set.
		"""
		if not isinstance(background_colour, Colour):
			background_colour = Colour(obj=background_colour)
		self._background_colour = background_colour

	@property
	def node_styles(self) -> Dict[str, NodeStyle]:
		"""
		Gets the styles of the nodes in the graph.

		Returns:
			Dict[str, NodeStyle]: The styles of the nodes in the graph.
		"""
		return {name: node.style for name, node in self.nodes_dict.items() if node.has_style()}

	@property
	def edge_styles(self) -> Dict[str, EdgeStyle]:
		"""
		Gets the styles of the edges in the graph.

		Returns:
			Dict[str, EdgeStyle]: The styles of the edges in the graph.
		"""
		return {edge.id: edge.style for node in self.nodes for edge in node.outward_edges if edge.has_style()}

	def stylize(self):
		"""Applies styles to the nodes and edges in the graph."""
		if self._global_node_style_overwrite is not None:
			smart_global_node_style_overwrite = None
			if 'shape' in self._global_node_style_overwrite:
				if self._global_node_style_overwrite['shape'].lower().startswith('auto'):
					if max([len(str(node.name)) for node in self.nodes]) < 3:
						smart_global_node_style_overwrite = self._global_node_style_overwrite.copy()
						smart_global_node_style_overwrite['shape'] = 'circle'
			if smart_global_node_style_overwrite is None:
				smart_global_node_style_overwrite = self._global_node_style_overwrite

			for node in self.nodes:
				node.style = smart_global_node_style_overwrite

		if self._global_edge_style_overwrite is not None:
			for edge in self.edges:
				edge.style = self._global_edge_style_overwrite

		if self._stylist == 'pensieve':
			stylize_with_pensieve(graph=self)
		elif self._stylist == 'random':
			stylize_randomly(graph=self)

		for name, style in self._node_style_overwrites.items():
			self.nodes_dict[name].style.complement(style)

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

		if self._global_node_style_overwrite is not None:
			smart_global_node_style_overwrite = None
			if 'shape' in self._global_node_style_overwrite:
				if self._global_node_style_overwrite['shape'].lower().startswith('auto'):
					if max([len(str(node.name)) for node in self.nodes]) < 3:
						smart_global_node_style_overwrite = self._global_node_style_overwrite.copy()
						smart_global_node_style_overwrite['shape'] = 'circle'
			if smart_global_node_style_overwrite is None:
				smart_global_node_style_overwrite = self._global_node_style_overwrite

			for node in self.nodes:
				node.style.complement(smart_global_node_style_overwrite)

		if self._global_edge_style_overwrite is not None:
			for edge in self.edges:
				edge.style.complement(self._global_edge_style_overwrite)

	def get_graphviz_header(
			self, dpi: int = 300, direction: Optional[str] = None, 
			height: Optional[Union[int, float]] = None, width: Optional[Union[int, float]] = None, 
			pad: Union[int, float] = DEFAULT_PAD
		) -> str:
		"""
		Generates the Graphviz header for the graph.

		Args:
			dpi (int): The DPI of the graph.
			direction (Optional[str]): The direction of the graph.
			height (Optional[Union[int, float]]): The height of the graph.
			width (Optional[Union[int, float]]): The width of the graph.
			pad (Union[int, float]): The padding of the graph.

		Returns:
			str: The Graphviz header.
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

		if self._tooltip is not None:
			attributes['tooltip'] = f'"{self._tooltip}"'

		#if dpi is not None:
		#	attributes['dpi'] = f'{dpi}'
		for key, value in self._kwargs.items():
			if isinstance(value, int):
				attributes[key] = value
			else:
				attributes[key] = f'"{value}"'

		if len(attributes) > 0:
			second_part += '\t graph [' + ', '.join([f'{key} = {value}' for key, value in attributes.items()]) + ' ];\n'

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

	def get_graphviz_str(
			self, direction: Optional[str] = None, 
			dpi: Optional[int] = 300, height: Optional[Union[int, float]] = None, width: Optional[Union[int, float]] = None, 
			pad: Union[int, float] = DEFAULT_PAD
		) -> str:
		"""
		Generates the Graphviz string representation of the graph.

		Args:
			direction (Optional[str]): The direction of the graph.
			dpi (Optional[int]): The DPI of the graph.
			height (Optional[Union[int, float]]): The height of the graph.
			width (Optional[Union[int, float]]): The width of the graph.
			pad (Union[int, float]): The padding of the graph.

		Returns:
			str: The Graphviz representation.
		"""
		direction = direction or self._direction

		nodes_str = '\t{\n\t\t' + '\n\t\t'.join([node.get_graphviz_str() for node in self.nodes_dict.values()]) + '\n\t}\n'
		edges_str = '\t' + '\n\t'.join([edge.get_graphviz_str() for edge in self.edges]) + '\n'
		header = self.get_graphviz_header(direction=direction, dpi=dpi, height=height, width=width, pad=pad)
		return header + nodes_str + edges_str + '}'

	def append(self, obj):
		"""
		Appends nodes and edges from an object's __graph__() method.

		Args:
			obj: The object to append to the graph.

		Returns:
			Graph: The updated graph.
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

			if 'label' in dictionary:
				self._label = '\n' + dictionary['label']

			if 'tooltip' in dictionary:
				self._tooltip = dictionary['tooltip']

			if 'label_url' in dictionary:
				self._label_url = dictionary['label_url']

			if 'global_node_style' in dictionary:
				self._global_node_style_overwrite = dictionary['global_node_style']
			elif 'graph_node_style' in dictionary:
				self._global_node_style_overwrite = dictionary['graph_node_style']

			if 'global_edge_style' in dictionary:
				self._global_edge_style_overwrite = dictionary['global_edge_style']
			elif 'graph_edge_style' in dictionary:
				self._global_edge_style_overwrite = dictionary['graph_edge_style']

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
	def from_dict(cls, obj: Dict) -> 'GraphWithoutDisplay':
		"""
		Creates a graph from a dictionary representation.

		Args:
			obj: The dictionary representation of the graph.

		Returns:
			Graph: The created graph.
		"""
		graph = cls()
		graph.append(obj=obj)
		return graph

	def __graph__(self) -> Dict:
		"""
		Returns the dictionary representation of the graph.

		Returns:
			Dict: The dictionary representation of the graph.
		"""
		nodes_dict = {}
		edges_list = []
		for node in self.nodes:
			nodes_dict[node.id] = {
				'label': node.display_label_or_value,
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
			'colour_scheme': self._colour_scheme,
			'label': self._label,
			'label_url': self._label_url,
			'node_styles': self._node_style_overwrites,
			'edge_styles': self._edge_style_overwrites,
			'global_node_style': self._global_node_style_overwrite,
			'global_edge_style': self._global_edge_style_overwrite,
			'node_colours': self._node_colour_overwrites,
			'nodes': nodes_dict,
			'edges': edges_list
		}

	@classmethod
	def random(
			cls, 
			num_nodes: int, 
			strict: bool = False, cycle: bool = False, start_index: int = 1, connection_probability: float = 0.5,
			ordering: bool = True, seed: Optional[int] = None
	):
		"""
		Creates a random graph.

		Args:
			num_nodes (int): The number of nodes in the graph.
			strict (bool): If True, the graph will be strict.
			cycle (bool): If True, the graph will be a cycle.
			start_index (int): The starting index of the nodes.
			connection_probability (float): The probability of a connection between two nodes.
			ordering (bool): If True, the graph will maintain ordering.
			seed (Optional[int]): The seed for the random number generator.

		Returns:
			GraphWithoutDisplay: The random graph.
		"""
		graph = cls(strict=strict, ordering=ordering)
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

	def __add__(self, other: 'GraphWithoutDisplay') -> 'GraphWithoutDisplay':
		"""
		Combines two graphs.

		Args:
			other: The other graph to combine with.

		Returns:
			GraphWithoutDisplay: The combined graph.
		"""
		return self.add(other=other)

	def add(self, other: 'GraphWithoutDisplay', add_values_function: Optional[Callable] = None) -> 'GraphWithoutDisplay':
		"""
		Combines two graphs.

		Args:
			other: The other graph to combine with.
			add_values_function: The function to add the values of the nodes.

		Returns:
			GraphWithoutDisplay: The combined graph.
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
			self, 
			path: Optional[str] = None, 
			view: bool = True, 
			direction: Optional[str] = None, 
			height: Optional[Union[int, float]] = None, 
			width: Optional[Union[int, float]] = None, 
			dpi: int = 300, 
			pad: Union[int, float] = DEFAULT_PAD
	) -> Union[Source, None]:
		"""
		Renders the graph and returns the Graphviz source.

		Args:
			path (Optional[str]): The path to save the graph.
			view (bool): Whether to view the graph.
			direction (Optional[str]): The direction of the graph.
			height (Optional[Union[int, float]]): The height of the graph.
			width (Optional[Union[int, float]]): The width of the graph.
			dpi (int): The DPI of the graph.
			pad (Union[int, float]): The padding of the graph.

		Returns:
			Union[Source, None]: The Graphviz source or None.
		"""
		direction = direction or self._direction

		self.stylize()

		if path is None:
			return self.get_graphviz_source(direction=direction, pad=pad, dpi=None)# Source(source=self.get_graphviz_str(direction=direction, pad=pad, dpi=None))
		else:
			filename, file_extension = os.path.splitext(path)
			output_format = file_extension.lstrip('.')
			to_save = self.get_graphviz_source(
				direction=direction, pad=pad, dpi=dpi, height=height, width=width, output_format=output_format
			)
			to_save.render(filename=filename, view=view)
			return self.get_graphviz_source(direction=direction, pad=pad, dpi=None)

	"""
	def display_html(self, direction=None, pad=None, echo_errors=False, **kwargs):
		try:
			return displayHTML(self.get_svg(direction=direction, pad=pad, **kwargs))
		except Exception as e:
			if echo_errors:
				print('Could not use displayHTML!')
				print(e)

			html = self.get_html(direction=direction, pad=pad, **kwargs)
			try:
				return display(html)
			except Exception as e:
				if echo_errors:
					print('Coult not use display!')
					print(e)
				from IPython.core.display import display as ipython_display
				return ipython_display(html)
	"""

	@staticmethod
	def _get_graphviz_source(string: str) -> Source:
		"""
		Converts a string to a Graphviz source.

		Args:
			string (str): The string to be converted.

		Returns:
			Source: The Graphviz source.
		"""
		if not isinstance(string, str):
			raise TypeError(f'string must be a string but is {type(string)}')
		return Source(source=string)

	def get_graphviz_source(
			self, 
			direction: Optional[str] = None, 
			dpi: Optional[int] = 300, 
			height: Optional[Union[int, float]] = None, 
			width: Optional[Union[int, float]] = None, 
			pad: Union[int, float] = DEFAULT_PAD, 
			output_format: Optional[str] = None
	) -> Source:
		"""
		Generates the Graphviz source for the graph.

		Args:
			direction (Optional[str]): The direction of the graph.
			dpi (Optional[int]): The DPI of the graph.
			height (Optional[Union[int, float]]): The height of the graph.
			width (Optional[Union[int, float]]): The width of the graph.
			pad (Union[int, float]): The padding of the graph.
			output_format (Optional[str]): The format of the graph.

		Returns:
			Source: The Graphviz source.
		"""
		if height is None and width is None:
			return self._get_graphviz_source(self.get_graphviz_str(direction=direction, pad=pad, dpi=None))
		else:
			graphviz_str_to_save = self.get_graphviz_str(
				direction=direction, height=height, width=width, pad=pad, dpi=dpi
			)
			return self._get_graphviz_source(graphviz_str_to_save)
