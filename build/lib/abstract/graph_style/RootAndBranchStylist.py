from .StyleMaster import StyleMaster
from .RootStylist import RootStylist
from .BranchStylist import BranchStylist
from .LoopStylist import LoopStylist
from .NodeStyle import NodeStyle


class RootAndBranchStylist(StyleMaster):
	def __init__(
			self, colour_scheme=None, node_style=None, font=None, node_shape=None,
			node_shape_style=None, edge_style=None, loop_node_style=None, loop_edge_style=None
	):
		self._colour_scheme = colour_scheme
		self._font = font
		self._node_shape = node_shape
		self._node_shape_style = node_shape_style
		self._node_style = node_style or NodeStyle(
			font=self._font, shape=self._node_shape, shape_style=self._node_shape_style
		)

		self._edge_style = edge_style

		super().__init__(
			stylists=[
				RootStylist(colour_scheme=self._colour_scheme, node_style=self._node_style),
				BranchStylist(edge_style=edge_style),
				LoopStylist(node_style=loop_node_style, edge_style=loop_edge_style)
			]
		)

	def copy(self):
		return self.__class__(
			colour_scheme=self._colour_scheme,
			node_style=self._node_style,
			font=self._font,
			node_shape=self._node_shape,
			node_shape_style=self._node_shape_style,
			edge_style=self._edge_style
		)
