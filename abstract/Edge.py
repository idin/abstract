from ._GraphObj import GraphObj
from .styling.EdgeStyle import EdgeStyle
from .Node import Node


class Edge(GraphObj):
	def __init__(
			self, graph, start, end, id=None, value=None, label=None, tooltip=None, style=None,
			**kwargs
	):
		"""
		:param Graph graph: a graph
		:param Node start: start node
		:param Node end: end node
		:param str or int id: an extra id (for when there are multiple edges between the same start and end nodes)
		:param value: some value the edge keeps
		:param str label: a label to show
		:param EdgeStyle or NoneType style: the style of the edge
		"""
		if style is None:
			style = EdgeStyle()
		elif isinstance(style, dict):
			style = EdgeStyle(**style)

		super().__init__(
			graph=graph, id=None, value=value, label=label, tooltip=tooltip, style=style,
			**kwargs
		)
		self._start = start
		self._end = end
		self.raw_id = id
		start.append_outward_edge(edge=self)
		end.append_inward_edge(edge=self)

	@property
	def style(self):
		"""
		:rtype: EdgeStyle
		"""
		return self._style

	@style.setter
	def style(self, style):
		"""
		:type style: EdgeStyle or dict
		"""
		if isinstance(style, dict):
			style = EdgeStyle(**style)
		self._style = style
		self._style_is_native = style is not None

	def is_similar_to(self, other):
		"""
		:type other: Edge
		:rtype: bool
		"""
		if not super().is_similar_to(other=other):
			return False
		return self._start.id == other._start.id and self._end.id == other._end.id and self.raw_id == other.raw_id

	def __getstate__(self):
		state = super().__getstate__()
		state.update({
			'start': None,
			'end': None,
			'id': self.raw_id
		})
		return state

	def __setstate__(self, state):
		super().__setstate__(state=state)
		self._start = state['start']
		self._end = state['end']
		self.raw_id = state['id']

	@property
	def id(self):
		if self._start is None:
			raise ValueError('This Edge does not have a start!')
		elif self._end is None:
			raise ValueError('This Edge does not have an end!')

		return self.start.id, self.end.id, self.raw_id

	def __str__(self):
		return f'Edge:{self.start}-{self.end}'

	def __repr__(self):
		return str(self)

	def get_graphviz_str(self):

		parts = []
		label_or_value = self.label_or_value
		style = self.style
		if label_or_value is not None:
			parts.append(f'label="{self.label_or_value}"')
		if self._tooltip is not None:
			parts.append(f'tooltip="{self._tooltip}"')
		if style is not None:
			parts.append(style.get_graphviz_str())

		if len(parts) > 0:
			second_part = '[' + ' '.join(parts) + ']'
		else:
			second_part = ''

		return f'"{self.start.name}" -> "{self.end.name}"' + second_part

	@property
	def start(self):
		"""
		:rtype: Node
		"""
		if self._start is None:
			raise ValueError('Edge does not have a start!')
		return self._start

	@property
	def end(self):
		"""
		:rtype: Node
		"""
		if self._end is None:
			raise ValueError('Edge does not have an end!')
		return self._end

	def remove_self(self):
		if self._start is None or self._end is None:
			raise ValueError('Either start or end Node is missing!')
		self.start.remove_outward_edge(edge_id=self.id)
		self.end.remove_inward_edge(edge_id=self.id)
		self._start = None
		self._end = None

	def is_in_loop(self):
		return self.start.is_in_loop_with(self.end)

	'''
	@property
	def graph_style(self):
		return self.graph.edge_style
	'''
