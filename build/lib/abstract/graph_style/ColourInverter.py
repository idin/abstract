from .StyleMaster import NodeStylist, EdgeStylist, StyleMaster
from .. import Graph

class NodeColourInverter(NodeStylist):
	def __init__(self):
		super().__init__(style=None, condition=None)

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype: Graph
		"""
		for node in graph.nodes:
			node.style = node.style.invert_colours()

		return graph

	def copy(self):
		return self.__class__()


class EdgeColourInverter(EdgeStylist):
	def __init__(self):
		super().__init__(style=None, condition=None)

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype: Graph
		"""
		for edge in graph.edges:
			edge.style = edge.style.invert_colours()

		return graph

	def copy(self):
		return self.__class__()


class ColourInverter(StyleMaster):
	def __init__(self):
		super().__init__(stylists=[NodeColourInverter(), EdgeColourInverter()])

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype: Graph
		"""

		for stylist in self.stylists:
			stylist.paint(graph=graph)
		graph.background_colour = graph.background_colour.invert()
		return graph

	def copy(self):
		return self.__class__()
