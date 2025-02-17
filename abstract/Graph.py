from ._GraphWithoutDisplay import GraphWithoutDisplay, DEFAULT_PAD
from typing import Optional, Union


class Graph(GraphWithoutDisplay):
	@staticmethod
	def _get_svg(source):
		try:
			return source._repr_svg_()
		except AttributeError:
			return source.pipe(format='svg', encoding=source._encoding)

	def get_svg(self, direction: Optional[str] = None, pad: Union[int, float] = DEFAULT_PAD, **kwargs) -> str:
		"""
		Generates the SVG representation of the graph.

		Args:
			direction (Optional[str]): The direction of the graph layout.
			pad (Union[int, float]): Padding around the graph.
			**kwargs: Additional keyword arguments for rendering.

		Returns:
			str: The SVG representation of the graph.
		"""
		source = self.render(direction=direction or self._direction, pad=pad, **kwargs)
		return Graph._get_svg(source)

	def _repr_html_(self) -> str:
		"""Returns the HTML representation of the graph."""
		return self.get_svg()

	def get_html(self, direction: Optional[str] = None, pad: Union[int, float] = DEFAULT_PAD, **kwargs) -> 'HTML':
		"""
		Generates the HTML representation of the graph.

		Args:
			direction (Optional[str]): The direction of the graph layout.
			pad (Union[int, float]): Padding around the graph.
			**kwargs: Additional keyword arguments for rendering.

		Returns:
			HTML: The HTML representation of the graph.
		"""
		from IPython.core.display import HTML
		return HTML(self.get_svg(direction=direction or self._direction, pad=pad, **kwargs))
