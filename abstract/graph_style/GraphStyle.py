from abstract.graph_style.GraphObjStyle import NodeStyle, EdgeStyle

from colouration import Scheme, Colour
DEFAULT_BACKGROUND_COLOUR = '#FAFAFA'
DEFAULT_COLOUR_SCHEME = 'pastel19'


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
		return self.edge_styles == other.edge_styles and \
			   self.node_styles == other.node_styles and \
			   self.background_colour == other.background_colour

	def __ne__(self, other):
		return not self.__eq__(other=other)
