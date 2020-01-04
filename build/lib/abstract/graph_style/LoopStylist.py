from .StyleMaster import NodeStylist, EdgeStylist, StyleMaster
from .NodeStyle import NodeStyle
from .EdgeStyle import EdgeStyle


class LoopNodeStylist(NodeStylist):
	def __init__(self, style=None):
		style = style or NodeStyle(fill_colour='yellow', border_colour='red', colour='red', shape='circle')
		super().__init__(style=style, condition=lambda node: node.is_in_loop())

	def copy(self):
		return self.__class__(style=self._style)


class LoopEdgeStylist(EdgeStylist):
	def __init__(self, style=None):
		style = style or EdgeStyle(colour='red')
		super().__init__(style=style, condition=lambda edge: edge.is_in_loop())

	def copy(self):
		return self.__class__(style=self._style)


class LoopStylist(StyleMaster):
	def __init__(self, node_style=None, edge_style=None):
		self._node_style = node_style
		self._edge_style = edge_style
		super().__init__(stylists=[LoopNodeStylist(style=node_style), LoopEdgeStylist(style=edge_style)])

	def copy(self):
		return self.__class__(node_style=self._node_style, edge_style=self._edge_style)
