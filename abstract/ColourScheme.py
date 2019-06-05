from colouration import Scheme, Colour


class ColourScheme:
	def __init__(
			self, node_colours=None, node_text_colours=None, node_fill_colours=None,
			edge_colours=None, edge_text_colours=None
	):
		self._node_colours = Scheme.auto(obj=node_colours, copy=False)
		self._node_text_colours = Scheme.auto(obj=node_text_colours or self._node_colours.darken(), copy=False)
		self._node_fill_colour = Scheme.auto(obj=node_fill_colours or self._node_colours.lighten(), copy=False)
		self._edge_colours = Scheme.auto(obj=edge_colours or self._node_colours, copy=False)
		self._edge_text_colours = Scheme.auto(obj=edge_text_colours or self._node_text_colours, copy=False)

	@property
	def node(self):
		"""
		:rtype: Scheme
		"""
		return self._node_colours

	@property
	def node_text(self):
		"""
		:rtype: Scheme
		"""
		return self._node_text_colours

	@property
	def node_fill(self):
		"""
		:rtype: Scheme
		"""
		return self._node_fill_colours

	@property
	def edge(self):
		"""
		:rtype: Scheme
		"""
		return self._edge_colours

	@property
	def edge_text(self):
		"""
		:rtype: Scheme
		"""
		return self._edge_text_colours

	def pick_node_colour(self, index=None):
		"""
		:type index: NoneType or int
		:rtype: Colour
		"""
		return self.node.pick(index=index)

	def pick_node_text_colour(self, index=None):
		"""
		:type index: NoneType or int
		:rtype: Colour
		"""
		return self.node_text.pick(index=index)

	def pick_node_fill_colour(self, index=None):
		"""
		:type index: NoneType or int
		:rtype: Colour
		"""
		return self.node_fill.pick(index=index)

	def pick_edge_colour(self, index=None):
		"""
		:type index: NoneType or int
		:rtype: Colour
		"""
		return self.edge.pick(index=index)

	def pick_edge_text_colour(self, index=None):
		"""
		:type index: NoneType or int
		:rtype: Colour
		"""
		return self.edge_text.pick(index=index)
