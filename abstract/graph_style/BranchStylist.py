from .StyleMaster import NodeStylist, EdgeStylist, StyleMaster
from .NodeStyle import NodeStyle
from .EdgeStyle import EdgeStyle
from .. import Node, Graph
from colouration import Colour
from .RootStylist import is_root_or_parents_are_in_loop


def get_style(node, pale_ratio, divergence_ratio, main_style):
	"""
	:type node: Node
	:rtype: NodeStyle
	"""
	if is_root_or_parents_are_in_loop(node):
		if main_style is None:
			return node.style.copy()
		else:
			return main_style.copy()
	else:
		if len(node.parents) == 1:
			parent = node.parents[0]
			num_siblings = len(parent.children)
			rank = node.get_child_rank(parent=parent)
			if main_style is None:
				style = get_style(
					node=parent, pale_ratio=pale_ratio, divergence_ratio=divergence_ratio, main_style=main_style
				)
			else:
				style = main_style
			if num_siblings == 0:
				colour = style.colour.copy(keep_id=True)
			else:
				colour = style.colour.increase_hue(
					amount=divergence_ratio * get_diverging_number(i=rank, n=num_siblings, reverse=False)
				)
			#colour = colour.pale(ratio=pale_ratio)
			colour.saturation = colour.saturation * 3 / 4
			new_style = style.copy()
			new_style.reset_colours()
			new_style.colour = colour
			return new_style
		else:
			styles = [
				get_style(node=parent, pale_ratio=pale_ratio, divergence_ratio=0, main_style=main_style)
				for parent in node.parents
				if not node.is_in_loop_with(parent)
			]
			colours = [style.colour for style in styles]
			if main_style is None:
				style = styles[0]
			else:
				style = main_style
			colour = Colour.mix(colours=colours).pale(ratio=pale_ratio)
			new_style = style.copy()
			new_style.reset_colours()
			new_style.colour = colour
			return new_style


def generate_diverging_numbers(n):
	if n == 1:
		return [0]
	elif n % 2 == 0:
		return [x/(n/2) for x in range(1, n // 2 + 1)] + [-x/(n/2) for x in range(1, n // 2 + 1)]
	else:
		return [0] + generate_diverging_numbers(n-1)


def get_diverging_number(i, n, reverse):
	return sorted(generate_diverging_numbers(n), reverse=reverse)[i]


class BranchNodeStylist(NodeStylist):
	def __init__(self, node_style=None, pale_ratio=0.05, divergence_ratio=0.05):
		self._divergence_ratio = divergence_ratio
		self._pale_ratio = pale_ratio
		self._node_style = node_style
		super().__init__(style=None, condition=None)

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype Graph
		"""

		for node in graph.nodes:
			if not is_root_or_parents_are_in_loop(node) and not node.is_in_loop():
				style = get_style(
					node=node, pale_ratio=self._pale_ratio, divergence_ratio=self._divergence_ratio,
					main_style=self._node_style
				)

				node.style = style
		return graph

	def copy(self):
		return self.__class__(pale_ratio=self._pale_ratio, divergence_ratio=self._divergence_ratio)


class BranchEdgeStylist(EdgeStylist):
	def __init__(self, edge_style=None):
		self._edge_style = edge_style
		super().__init__(style=None, condition=None)

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype Graph
		"""

		for edge in graph.edges:
			colour = edge.start.style.colour.darken(ratio=0.1)

			if self._edge_style is None:
				edge_style = EdgeStyle(colour=colour)
			else:
				edge_style = self._edge_style.copy()
				edge_style.reset_colours()
				edge_style.colour = colour

			if edge.value is not None:
				edge_style._arrow_size *= edge.value

			edge.style = edge_style
		return graph

	def copy(self):
		return self.__class__(edge_style=self._edge_style)


class BranchStylist(StyleMaster):
	def __init__(self, node_style=None, pale_ratio=0.05, divergence_ratio=0.05, edge_style=None):
		self._node_style = node_style
		self._pale_ratio = pale_ratio
		self._divergence_ratio = divergence_ratio
		self._edge_style = edge_style
		super().__init__(stylists=[
			BranchNodeStylist(node_style=node_style, pale_ratio=pale_ratio, divergence_ratio=divergence_ratio),
			BranchEdgeStylist(edge_style=edge_style)
		])

	def copy(self):
		return self.__class__(
			node_style=self._node_style, pale_ratio=self._pale_ratio, divergence_ratio=self._divergence_ratio,
			edge_style=self._edge_style
		)
