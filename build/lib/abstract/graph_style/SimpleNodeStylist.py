from .. import Graph
from copy import deepcopy
from .NodeStyle import NodeStyle


class SimpleNodeStylist:
	def __init__(self, style, condition=None):
		"""
		:type style: callable or NodeStyle
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
			def paint_node(node):
				style(node)

		else:
			def paint_node(node):
				node.style = style

		self._paint_node = paint_node

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype Graph
		"""
		for node in graph.nodes:
			if self._condition_function(node):
				self._paint_node(node=node)

		return graph

	def copy(self):
		"""
		:rtype: SimpleNodeStylist
		"""
		return self.__class__(style=deepcopy(self._style), condition=deepcopy(self._condition))
