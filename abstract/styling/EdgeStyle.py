from colouration import Colour


DEFAULT_COLOUR = Colour(hexadecimal='#AAAAAA')
DEFAULT_EDGE_TEXT_SIZE = 8
DEFAULT_ARROW_SIZE = 0.5
DEFAULT_FONT = 'helvetica'
DEFAULT_NODE_COLOUR_DIFFERENCE_RATIO = 0.5
DEFAULT_EDGE_OPACITY = 1
DEFAULT_EDGE_LABEL_STYLE = 'below'


class EdgeStyle:
	def __init__(
			self, colour=DEFAULT_COLOUR, opacity=DEFAULT_EDGE_OPACITY,
			font=DEFAULT_FONT, text_colour=None, text_size=DEFAULT_EDGE_TEXT_SIZE,
			arrow_size=DEFAULT_ARROW_SIZE, label_style=DEFAULT_EDGE_LABEL_STYLE,
			line_width=1
	):
		colour = colour or text_colour or DEFAULT_COLOUR
		colour = Colour(colour)
		self._colour = colour
		self._text_colour = None

		self._text_colour_based_on_main_colour = False

		self.text_colour = text_colour
		self.colour = colour

		self._opacity = opacity
		self._font = font
		self._text_size = text_size
		self._arrow_size = arrow_size
		self._label_style = label_style
		self._line_width = line_width

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
				raise ValueError(f'{key} is not a valid attribute of EdgeStyle')

	def reset_colours(self):
		self._text_colour = None

	def copy(self):
		"""
		:rtype: EdgeStyle
		"""
		result = self.__class__(
			colour=self._colour, opacity=self._opacity,
			font=self._font, text_colour=self._text_colour, text_size=self._text_size,
			arrow_size=self._arrow_size, line_width=self._line_width
		)
		result._text_colour_based_on_main_colour = self._text_colour_based_on_main_colour
		return result

	def invert_colours(self):
		"""
		:rtype: EdgeStyle
		"""
		result = self.copy()

		if result._text_colour_based_on_main_colour:
			result._text_colour = None
		else:
			result.text_colour = result.text_colour.invert()

		if result.colour is not None:
			result.colour = result.colour.invert()

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
		if self._text_colour is None:
			self._text_colour = colour
			self._text_colour_based_on_main_colour = True

	@property
	def text_colour(self):
		"""
		:rtype: Colour
		"""
		return self._text_colour or self.colour

	@text_colour.setter
	def text_colour(self, text_colour):
		if text_colour is None:
			if self.colour is not None:
				self._text_colour = self.colour
				self._text_colour_based_on_main_colour = True
		else:
			self._text_colour = Colour(text_colour)
			self._text_colour_based_on_main_colour = False

	def __getstate__(self):
		return {
			'_colour': self._colour,
			'_opacity': self._opacity,
			'_font': self._font,
			'_text_colour': self._text_colour,
			'_text_size': self._text_size,
			'_arrow_size': self._arrow_size,
			'_label_style': self._label_style,
			'_line_width': self._line_width
		}

	def __setstate__(self, state):
		self._colour = state['_colour']
		self._opacity = state['_opacity']
		self._font = state['_font']
		self._text_colour = state['_text_colour']
		self._text_size = state['_text_size']
		self._arrow_size = state['_arrow_size']
		self._label_style = state['_label_style']
		self._line_width = state['_line_width']

	@property
	def _graphviz_dictionary(self):
		return {
			'color': self.colour,
			'fontname': self._font,
			'fontcolor': self.text_colour,
			'fontsize': self._text_size,
			'arrowsize': self._arrow_size,
			'lblstyle': self._label_style,
			'penwidth': self._line_width
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
