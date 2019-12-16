from .. import Graph
from copy import deepcopy
from .EdgeStyle import EdgeStyle


class SimpleEdgeStylist:
	def __init__(self, style, condition=None):
		"""
		:type style: callable or EdgeStyle
		:type condition: callable or NoneType
		"""
		self._condition = condition
		self._style = style

		if condition is None:
			def condition_function(node):
				return True
		elif not callable(condition):
			raise TypeError(f'condition should either be None or a function, but it is a {type(condition)}')
		else:
			condition_function = condition

		self._condition_function = condition_function

		if callable(style):
			def paint_edge(edge):
				style(edge)

		else:
			def paint_edge(edge):
				edge.style = style

		self._paint_edge = paint_edge

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype Graph
		"""

		for edge in graph.edges:
			if self._condition_function(edge):
				self._paint_edge(edge=edge)

		return graph

	def copy(self):
		"""
		:rtype: SimpleNodeStylist
		"""
		return self.__class__(style=deepcopy(self._style), condition=deepcopy(self._condition))
