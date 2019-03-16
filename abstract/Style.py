STYLE_RENAME = {
	'colour': 'color',
	'fill_colour': 'fillcolor',
	'text_colour': 'fontcolor',
	'text_size': 'fontsize',
	'font': 'fontname',
	#'label_style': 'lblstyle',
	'arrow_size': 'arrowsize'

}


class Style:
	def __init__(self, **kwargs):

		self._dictionary = kwargs
		for old_key, new_key in STYLE_RENAME.items():
			if old_key in self.dictionary:
				self._dictionary[new_key] = self._dictionary.pop(old_key)

	@property
	def dictionary(self):
		return self._dictionary.copy()

	def copy(self):
		result = self.__class__()
		result._dictionary = self.dictionary
		return result

	def update(self, other, inplace=False):
		"""
		:param Style or dict other: another style or dictionary that would update this one
		:param bool inplace: if this object should be updated or a new one created
		:rtype: NoneType or Style
		"""
		if inplace:
			if isinstance(other, Style):
				self._dictionary.update(other.dictionary)
			elif isinstance(other, dict):
				self._dictionary.update(other)
		else:
			result = self.copy()
			result.update(other=other, inplace=True)
			return result

	def set(self, **kwargs):
		d = kwargs
		for old_key, new_key in STYLE_RENAME.items():
			if old_key in d:
				d[new_key] = d.pop(old_key)
		self.update(d, inplace=True)

	def get_graphviz_str(self):
		return ' '.join([f'{key}={value}' for key, value in self._dictionary.items() if value is not None])


class EdgeStyle(Style):
	def __init__(
			self,
			colour='darkseagreen3', arrow_size=0.5,
			text_colour='darkseagreen4', font='helvetica', text_size=8, #label_style='"above, sloped"',
			**kwargs
	):
		kwargs.update({
			'colour': colour, 'arrow_size': arrow_size,
			'text_colour': text_colour, 'font': font, 'text_size': text_size, #'label_style': label_style
		})
		super().__init__(**kwargs)


class NodeStyle(Style):
	def __init__(
			self,
			colour='gray80',
			text_colour='deepskyblue2', text_size=10, font='helvetica',
			fill_colour='gray95', shape='egg', style='filled',
			**kwargs
	):
		kwargs.update({
			'colour': colour, 'text_colour': text_colour, 'fill_colour': fill_colour,
			'text_size': text_size, 'font': font, 'shape': shape, 'style': style
		})
		super().__init__(**kwargs)






