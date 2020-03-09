from .StyleMaster import NodeStylist
from .NodeStyle import NodeStyle
from .. import Node
from colouration import Scheme
DEFAULT_COLOUR_SCHEME = 'pastel15'


def is_root_or_parents_are_in_loop(node):
	"""
	:type node: Node
	:rtype: bool
	"""
	parents = [parent for parent in node.parents if not parent.is_in_loop()]
	return len(parents) == 0


class RootStylist(NodeStylist):
	def __init__(self, node_style=None, colour_scheme=None, strict=False):
		"""
		:type colour_scheme: Scheme or NoneType or str
		"""
		self._strict = strict # strict means number of descendants is also important
		self._node_style = node_style

		if isinstance(colour_scheme, str):
			colour_scheme = Scheme(name=colour_scheme)
		elif colour_scheme is None:
			colour_scheme = Scheme(name=DEFAULT_COLOUR_SCHEME)

		self._colour_scheme = colour_scheme
		self._colours_used = {colour: 0 for colour in self._colour_scheme.colours}

		super().__init__(style=None, condition=is_root_or_parents_are_in_loop)

	def _get_least_used_colour(self, usage=1):
		colour = min(self._colours_used, key=self._colours_used.get)
		self._use_colour(colour=colour, usage=usage)
		return colour

	def _use_colour(self, colour, usage=1):
		self._colours_used[colour] += usage

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype Graph
		"""

		for node in graph.nodes:
			if self._condition_function(node):
				if self._strict:
					usage = node.num_descendants
				else:
					usage = 1

				colour = self._get_least_used_colour(usage=usage)
				if self._node_style is None:
					style = NodeStyle(colour=colour)
				else:
					style = self._node_style.copy()
					style.reset_colours()
					style.colour = colour

				node.style = style

		return graph

	def copy(self):
		return self.__class__(colour_scheme=self._colour_scheme, strict=self._strict)
