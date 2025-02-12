from ._GraphObj import GraphObj
from .styling.EdgeStyle import EdgeStyle
from .Node import Node
from typing import Optional, Union, Dict, Tuple


class Edge(GraphObj):
	def __init__(
			self, graph: 'Graph', start: Node, end: Node, id: Optional[Union[str, int]] = None, 
			value: Optional[object] = None, label: Optional[str] = None, 
			tooltip: Optional[str] = None, style: Optional[EdgeStyle] = None, **kwargs
	):
		"""
		Initializes an Edge instance.

		Args:
			graph (Graph): A graph.
			start (Node): Start node.
			end (Node): End node.
			id (Optional[Union[str, int]]): An extra ID (for when there are multiple edges between the same start and end nodes).
			value (Optional[object]): Some value the edge keeps.
			label (Optional[str]): A label to show.
			tooltip (Optional[str]): Tooltip for the edge.
			style (Optional[EdgeStyle]): The style of the edge.
			**kwargs: Additional keyword arguments.
		"""

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
	def _label_converter(self):
		"""Gets the label converter for the edge."""
		return self.graph._edge_label_converter

	@property
	def style(self) -> Optional[EdgeStyle]:
		"""
		Gets the style of the edge.

		Returns:
			Optional[EdgeStyle]: The style of the edge.
		"""
		return self._style

	@style.setter
	def style(self, style: Union[EdgeStyle, Dict]):
		"""
		Sets the style of the edge.

		Args:
			style (Union[EdgeStyle, Dict]): The style to set, can be an EdgeStyle instance or a dictionary.
		
		Raises:
			RuntimeError: If overwriting the style is not allowed.
			TypeError: If the style type is not supported.
		"""
		if self._style is not None and not self.graph._style_overwrite_allowed:
			raise RuntimeError('Cannot overwrite edge style!')

		if isinstance(style, dict):
			self._style = EdgeStyle(**style)
		elif isinstance(style, EdgeStyle):
			self._style = style
		elif style is None:
			pass
		else:
			raise TypeError(f'edge style of type {type(style)} is not supported!')

	def is_similar_to(self, other: 'Edge') -> bool:
		"""
		Checks if this edge is similar to another edge.

		Args:
			other (Edge): The other edge to compare.

		Returns:
			bool: True if similar, False otherwise.
		"""
		if not super().is_similar_to(other=other):
			return False
		return (self._start.id == other._start.id and 
				self._end.id == other._end.id and 
				self.raw_id == other.raw_id)

	def __getstate__(self) -> Dict:
		"""Returns the state of the edge for pickling."""
		state = super().__getstate__()
		state.update({
			'start': None,
			'end': None,
			'id': self.raw_id
		})
		return state

	def __setstate__(self, state: Dict):
		"""Restores the state of the edge from a pickled state."""
		super().__setstate__(state=state)
		self._start = state['start']
		self._end = state['end']
		self.raw_id = state['id']

	@property
	def id(self) -> Tuple[Union[str, int]]:
		"""
		Gets the ID of the edge.

		Returns:
			Tuple[Union[str, int]]: The ID of the edge.
		
		Raises:
			ValueError: If the edge does not have a start or end.
		"""
		if self._start is None:
			raise ValueError('This Edge does not have a start!')
		elif self._end is None:
			raise ValueError('This Edge does not have an end!')

		return self.start.id, self.end.id, self.raw_id

	def __str__(self) -> str:
		"""Returns a string representation of the edge."""
		return f'Edge:{self.start}-{self.end}'

	def __repr__(self) -> str:
		"""Returns a string representation of the edge for debugging."""
		return str(self)

	def get_graphviz_str(self) -> str:
		"""
		Gets the Graphviz string representation of the edge.

		Returns:
			str: The Graphviz representation.
		"""
		parts = []
		label_or_value = self.display_label_or_value()
		style = self.style
		if label_or_value is not None:
			parts.append(f'label="{label_or_value}"')
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
	def start(self) -> Node:
		"""
		Gets the start node of the edge.

		Returns:
			Node: The start node.

		Raises:
			ValueError: If the edge does not have a start.
		"""
		if self._start is None:
			raise ValueError('Edge does not have a start!')
		return self._start

	@property
	def end(self) -> Node:
		"""
		Gets the end node of the edge.

		Returns:
			Node: The end node.

		Raises:
			ValueError: If the edge does not have an end.
		"""
		if self._end is None:
			raise ValueError('Edge does not have an end!')
		return self._end

	def remove_self(self):
		"""Removes the edge from its start and end nodes."""
		if self._start is None or self._end is None:
			raise ValueError('Either start or end Node is missing!')
		self.start.remove_outward_edge(edge_id=self.id)
		self.end.remove_inward_edge(edge_id=self.id)
		self._start = None
		self._end = None
		self._graph = None

	def is_in_loop(self) -> bool:
		"""Checks if the edge is in a loop."""
		return self.start.is_in_loop_with(self.end)

	# TODO: Uncomment if needed
	# @property
	# def graph_style(self):
	#     return self.graph.edge_style
