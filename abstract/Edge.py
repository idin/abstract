from .GraphObj import GraphObj
from .Style import EdgeStyle
from .Node import Node


class Edge(GraphObj):
	def __init__(self, graph, start, end, id=None, value=None, label=None, style=None, **kwargs):
		"""
		:param Graph graph: a graph
		:param Node start: start node
		:param Node end: end node
		:param str or int id: an extra id (for when there are multiple edges between the same start and end nodes)
		:param value: some value the edge keeps
		:param str label: a label to show
		:param EdgeStyle or NoneType style: the style of the edge
		"""
		super().__init__(graph=graph, id=None, value=value, label=label, style=style, **kwargs)
		self._start = start
		self._end = end
		self._id = id
		start.append_outward_edge(edge=self)
		end.append_inward_edge(edge=self)

	def is_similar_to(self, other):
		"""
		:type other: Edge
		:rtype: bool
		"""
		if not super().is_similar_to(other=other):
			return False
		return self._start._id == other._start._id and self._end._id == other._end._id and self._id == other._id

	def __getstate__(self):
		state = super().__getstate__()
		state.update({
			'start': None,
			'end': None,
			'id': self._id
		})
		return state

	def __setstate__(self, state):
		super().__setstate__(state=state)
		self._start = state['start']
		self._end = state['end']
		self._id = state['id']

	@property
	def style(self):
		"""
		:rtype: EdgeStyle
		"""
		if self._style is None:
			return self.graph.get_edge_style(style_name='default', node_name=self.start.name)
		elif isinstance(self._style, str):
			return self.graph.get_edge_style(style_name=self._style, node_name=self.start.name)
		else:
			raise TypeError(f'edge.style is of type {type(self._style)}')

	@style.setter
	def style(self, style):
		if style is None:
			self._style = None
		else:
			if isinstance(style, dict):
				the_style = EdgeStyle(**style)
			elif isinstance(style, EdgeStyle):
				the_style = style.copy()
			elif isinstance(style, str):
				the_style = self.graph._edge_styles[style]
			else:
				raise TypeError(f'edge.style is of type {type(style)}')

			if the_style.name is None:
				the_style._name = str(self.id)
			self.graph._edge_styles[the_style.name] = the_style
			self._style = the_style.name

	@property
	def id(self):
		if self._start is None:
			raise ValueError('This Edge does not have a start!')
		elif self._end is None:
			raise ValueError('This Edge does not have an end!')

		return self.start.id, self.end.id, self._id

	def __str__(self):
		return f'Edge:{self.start}-{self.end}'

	def __repr__(self):
		return str(self)

	def get_graphviz_style_str(self):
		if self.style is None:
			return ''
		else:
			return self.style.get_graphviz_str()

	def get_graphviz_label_str(self):
		if self.label_or_value is None:
			return ''
		else:
			return f'label="{self.label_or_value}"'

	def get_graphviz_str(self):
		without_style = f'"{self.start.name}" -> "{self.end.name}"'
		style = self.get_graphviz_style_str()
		label = self.get_graphviz_label_str()
		if style == '' and label == '':
			return without_style
		elif style == '':
			return f'{without_style} [{label}]'
		elif label == '':
			return f'{without_style} [{style}]'
		else:
			return f'{without_style} [{label} {style}]'

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

