from .NodeStyle import NodeStyle
from .EdgeStyle import EdgeStyle

from colouration import Scheme, Colour
DEFAULT_BACKGROUND_COLOUR = '#FAFAFA'
DEFAULT_COLOUR_SCHEME = 'pastel15'


class GraphStyle:
	def __init__(self, graph):
		self._node_colour_indices = None
		self._node_styles = {}
		self._edge_styles = {}
		self._colour_scheme = None
		self._node_styles_counter = {}
		self._edge_styles_counter = {}
		self._background_colour = None
		self._graph = graph
		self.add_colours(
			name='default', colour_scheme=DEFAULT_COLOUR_SCHEME, background_colour=DEFAULT_BACKGROUND_COLOUR
		)

	def __getstate__(self):
		return {
			'node_styles': self._node_styles,
			'edge_styles': self._edge_styles,
			'node_styles_counter': self._node_styles_counter,
			'edge_styles_counter': self._edge_styles_counter,
			'node_colour_indices': self._node_colour_indices,
			'background_colour': self._background_colour
		}

	def __setstate__(self, state):
		self._node_styles = state['node_styles']
		self._edge_styles = state['edge_styles']
		self._node_styles_counter = state['node_styles_counter']
		self._edge_styles_counter = state['edge_styles_counter']
		self._node_colour_indices = state['node_colour_indices']
		self._background_colour = state['background_colour']

	@property
	def graph(self):
		"""
		:rtype: .Graph.Graph
		"""
		return self._graph

	def reset_node_colours(self):
		self._node_colour_indices = None

	def add_colours(self, name, colour_scheme, background_colour):
		colour_scheme = Scheme.auto(obj=colour_scheme or DEFAULT_COLOUR_SCHEME)
		self._background_colour = Colour.auto(obj=background_colour)
		self._node_styles[name] = [
			create_node_colour_inheritance_style(colour=colour)
			for colour in colour_scheme.colours
		]
		self._edge_styles[name] = [
			inherit_colour_from_start_node
			for colour in colour_scheme.colours
		]

	def get_node_style(self, style_name, number=None, node_name=None):
		node_style = self._node_styles[style_name]
		if isinstance(node_style, NodeStyle):
			return node_style
		else:
			if number is None:
				number = self.node_colour_indices[node_name]
			return node_style[number % len(node_style)]

	def get_edge_style(self, style_name, number=None, node_name=None):
		edge_style = self._edge_styles[style_name]
		if isinstance(edge_style, EdgeStyle):
			return edge_style
		else:
			if number is None:
				number = self.node_colour_indices[node_name]
			return edge_style[number % len(edge_style)]

	@property
	def node_colour_indices(self):
		if self._node_colour_indices is None:
			sorted_nodes = [
				name for name, _ in sorted(
					self.graph.nodes_dict.items(),
					key=lambda name_node: (-name_node[1].num_outward_edges, name_node[1].index)
				)
			]
			self._node_colour_indices = {name: index for index, name in enumerate(sorted_nodes)}

		return self._node_colour_indices

	@property
	def node_styles(self):
		"""
		:rtype: dict[NodeStyle]
		"""
		return self._node_styles

	@property
	def edge_styles(self):
		"""
		:rtype: dict[EdgeStyle]
		"""
		return self._edge_styles

	@property
	def background_colour(self):
		"""
		:rtype: Colour
		"""
		return self._background_colour

	def __eq__(self, other):
		"""
		:type other: GraphStyle
		:rtype: bool
		"""
		condition_1 = self.edge_styles == other.edge_styles
		condition_2 = self.node_styles == other.node_styles
		condition_3 = self.background_colour == other.background_colour
		return condition_1 and condition_2 and condition_3

	def __ne__(self, other):
		return not self.__eq__(other=other)
