from ._GraphWithoutDisplay import GraphWithoutDisplay, DEFAULT_PAD


class Graph(GraphWithoutDisplay):
	def get_svg(self, direction=None, pad=DEFAULT_PAD, **kwargs):
		"""
		:type direction: NoneType or str
		:type pad: NoneType or int or float
		:rtype: str
		"""
		source =  self.render(direction=direction or self._direction, pad=pad, **kwargs)
		try:
			return source._repr_svg_()
		except AttributeError:
			return source.pipe(format='svg', encoding=source._encoding)

	def _repr_html_(self):
		return self.get_svg()

	def get_html(self, direction=None, pad=DEFAULT_PAD, **kwargs):
		from IPython.core.display import HTML
		return HTML(self.get_svg(direction=direction or self._direction, pad=pad, **kwargs))
