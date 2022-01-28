from colouration import Colour


DEFAULT_COLOUR = Colour(hexadecimal='#AAAAAA')
DEFAULT_TEXT_SIZE = 10
DEFAULT_FONT = 'helvetica'
DEFAULT_SHAPE = 'box'
DEFAULT_SHAPE_STYLE = 'rounded, filled'
DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO = 0.5


class NodeStyle:
	def __init__(
			self, colour=DEFAULT_COLOUR, fill_colour=None, border_colour=None, opacity=None,
			font=DEFAULT_FONT, text_colour=None, text_size=DEFAULT_TEXT_SIZE,
			shape=DEFAULT_SHAPE, shape_style=DEFAULT_SHAPE_STYLE, lighter_fill=True
	):
		colour = colour or fill_colour or border_colour or DEFAULT_COLOUR
		colour = Colour(obj=colour)

		self._fill_colour_based_on_main_colour = False
		self._border_colour_based_on_main_colour = False
		self._text_colour_based_on_main_colour = False
		self._lighter_fill = lighter_fill

		self._colour = colour
		self._fill_colour = None
		self._border_colour = None
		self._text_colour = None

		self.fill_colour = fill_colour
		self.border_colour = border_colour
		self.text_colour = text_colour
		self.colour = colour

		self._opacity = opacity
		self._font = font
		self._text_size = text_size
		self._shape = shape
		self._shape_style = shape_style

	def complement(self, dictionary):
		"""
		:type dictionary: dict
		"""
		for key, value in dictionary.items():
			if hasattr(self, key):
				setattr(self, key, value)
			elif not key.startswith('_'):
				setattr(self, f'_{key}', value)
			else:
				raise ValueError(f'{key} is not a valid attribute of NodeStyle')

	def reset_colours(self):
		self._fill_colour = None
		self._border_colour = None
		self._text_colour = None

	def invert_colours(self):
		"""
		:rtype: NodeStyle
		"""
		result = self.copy()

		if result._fill_colour_based_on_main_colour:
			result._fill_colour = None
		else:
			result.fill_colour = result.fill_colour.invert()

		if result._text_colour_based_on_main_colour:
			result._text_colour = None
		else:
			result.text_colour = result.text_colour.invert()

		if result._border_colour_based_on_main_colour:
			result._border_colour = None
		else:
			result.border_colour = result.border_colour.invert()

		if result.colour is not None:
			result.colour = result.colour.invert()

		return result

	def copy(self):
		"""
		:rtype: NodeStyle
		"""
		result = self.__class__(
			colour=self._colour, fill_colour=self._fill_colour, border_colour=self._border_colour,
			opacity=self._opacity, font=self._font, text_colour=self._text_colour, text_size=self._text_size,
			shape=self._shape, shape_style=self._shape_style
		)
		result._fill_colour_based_on_main_colour = self._fill_colour_based_on_main_colour
		result._text_colour_based_on_main_colour = self._text_colour_based_on_main_colour
		result._border_colour_based_on_main_colour = self._border_colour_based_on_main_colour
		return result

	@property
	def colour(self):
		"""
		:rtype: Colour
		"""
		return self._colour

	@colour.setter
	def colour(self, colour):
		if isinstance(colour, str):
			colour = Colour(obj=colour)
		self._colour = colour
		if self._fill_colour is None:
			if self._lighter_fill:
				self._fill_colour = colour.lighten(ratio=DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO)
			else:
				self._fill_colour = colour.darken(ratio=DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO)
			self._fill_colour_based_on_main_colour = True
		if self._border_colour is None:
			if self._lighter_fill:
				self._border_colour = colour.darken(ratio=DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO / 3)
			else:
				self._border_colour = colour.lighten(ratio=DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO / 3)
			self._border_colour_based_on_main_colour = True
		if self._text_colour is None:
			self._text_colour = self.fill_colour.farthest_gray
			self._text_colour_based_on_main_colour = True

	@property
	def fill_colour(self):
		"""
		:rtype: Colour
		"""
		return self._fill_colour

	@fill_colour.setter
	def fill_colour(self, fill_colour):
		if fill_colour is None:
			self._fill_colour = None
			if self.colour is not None:
				self._fill_colour = self.colour
				self._fill_colour_based_on_main_colour = True
		else:
			self._fill_colour = Colour(fill_colour)
			self._fill_colour_based_on_main_colour = False

	@property
	def border_colour(self):
		"""
		:rtype: Colour
		"""
		return self._border_colour

	@border_colour.setter
	def border_colour(self, border_colour):
		if border_colour is None:
			if self.colour is not None:
				self._border_colour = self.colour.darken_or_lighten(ratio=DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO)
				self._border_colour_based_on_main_colour = True
		else:
			self._border_colour = Colour(border_colour)
			self._border_colour_based_on_main_colour = False

	@property
	def text_colour(self):
		"""
		:rtype: Colour
		"""
		return self._text_colour

	@text_colour.setter
	def text_colour(self, text_colour):
		if text_colour is None:
			if self.fill_colour is not None:
				self._text_colour = self.fill_colour.farthest_gray
				self._text_colour_based_on_main_colour = True
			elif self.colour is not None:
				self._text_colour = self.colour.farthest_gray
				self._text_colour_based_on_main_colour = True
		else:
			self._text_colour = Colour(text_colour)
			self._text_colour_based_on_main_colour = False

	def __getstate__(self):
		return {
			'_colour': self._colour,
			'_fill_colour': self._fill_colour,
			'_border_colour': self._border_colour,
			'_font': self._font,
			'_text_colour': self._text_colour,
			'_text_size': self._text_size,
			'_shape': self._shape,
			'_shape_style': self._shape_style
		}

	def __setstate__(self, state):
		self._colour = state['_colour']
		self._fill_colour = state['_fill_colour']
		self._border_colour = state['_border_colour']
		self._opacity = state['_opacity']
		self._font = state['_font']
		self._text_colour = state['_text_colour']
		self._text_size = state['_text_size']
		self._shape = state['_shape']
		self._shape_style = state['_shape_style']

	@property
	def _graphviz_dictionary(self):
		return {
			'color': self.border_colour,
			'fillcolor': self.fill_colour,
			'fontname': self._font,
			'fontcolor': self.text_colour,
			'fontsize': self._text_size,
			'opacity': self._opacity,
			'shape': self._shape,
			'style': self._shape_style
		}

	def get_graphviz_str(self):
		"""
		:rtype: str
		"""
		key_values = []
		for key, value in self._graphviz_dictionary.items():
			if isinstance(value, Colour):
				value = value.get_hexadecimal(opacity=self._opacity)

			if isinstance(key, str):
				key = key.strip('"')

			if isinstance(value, str):
				value = value.strip('"')

			if value is not None:
				key_values.append((key, value))

		return ' '.join([f'"{key}"="{value}"' for key, value in key_values])
