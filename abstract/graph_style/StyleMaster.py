from .. import Graph
from .SimpleEdgeStylist import SimpleEdgeStylist
from .SimpleNodeStylist import SimpleNodeStylist


class EdgeStylist(SimpleEdgeStylist):
	def __add__(self, other):
		"""
		:type other: EdgeStylist or NodeStylist or StyleMaster
		:rtype: StyleMaster
		"""
		if isinstance(other, StyleMaster):
			return StyleMaster(stylists=[self] + StyleMaster.stylists)
		else:
			return StyleMaster(stylists=[self, other])


class NodeStylist(SimpleNodeStylist):
	def __add__(self, other):
		"""
		:type other: EdgeStylist or NodeStylist or StyleMaster
		:rtype: StyleMaster
		"""
		if isinstance(other, StyleMaster):
			return StyleMaster(stylists=[self] + StyleMaster.stylists)
		else:
			return StyleMaster(stylists=[self, other])


class StyleMaster:
	def __init__(self, stylists=None):
		"""
		:type stylists: list[EdgeStylist or NodeStylist or StyleMaster] or NoneType
		"""

		if stylists is None:
			stylists = []

		self._stylists = []
		for stylist in stylists:
			if hasattr(stylist, 'paint'):
				self._stylists.append(stylist.copy())
			else:
				raise TypeError(f'stylist is of type {type(stylist)}')

	@property
	def stylists(self):
		"""
		:rtype: list[SimpleEdgeStylist or SimpleNodeStylist]
		"""
		return self._stylists

	def paint(self, graph):
		"""
		:type graph: Graph
		:rtype Graph
		"""
		for stylist in self.stylists:
			stylist.paint(graph=graph)

		return graph

	def copy(self):
		"""
		:rtype: StyleMaster
		"""
		return self.__class__(stylists=[stylist.copy() for stylist in self.stylists])

	def __add__(self, other):
		"""
		:type other: StyleMaster or EdgeStylist or NodeStylist
		:rtype StyleMaster
		"""
		if isinstance(other, self.__class__):
			return self.__class__(stylists=[stylist.copy() for stylist in self.stylists + other.stylists])
		else:
			return self.__class__(stylists=[stylist.copy() for stylist in self.stylists + [other]])
