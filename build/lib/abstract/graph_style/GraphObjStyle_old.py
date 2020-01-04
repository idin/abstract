from colouration import Colour


STYLE_RENAME = {
	'colour': 'color',
	'fill_colour': 'fillcolor',
	'text_colour': 'fontcolor',
	'text_size': 'fontsize',
	'font': 'fontname',
	# 'label_style': 'lblstyle',
	'arrow_size': 'arrowsize'

}


class GraphObjStyle:
	def __init__(self, name=None, opacity=None, **kwargs):
		self._name = name,
		self._opacity = opacity
		self._dictionary = kwargs
		self.update_dictionary_keys()

	def update_dictionary_keys(self):
		for old_key, new_key in STYLE_RENAME.items():
			if old_key in self.dictionary:
				self._dictionary[new_key] = self._dictionary.pop(old_key)

	def __getstate__(self):
		return {
			'name': self._name,
			'dictionary': self._dictionary
		}

	def __setstate__(self, state):
		self._name = state['name']
		self._dictionary = state['dictionary']
		self.update_dictionary_keys()

	@property
	def name(self):
		"""
		:rtype: str or NoneType
		"""
		if self._name is not None:
			return str(self._name)
		else:
			return None

	def __eq__(self, other):
		"""
		:type other: GraphObjStyle
		:rtype: bool
		"""
		return self._dictionary == other._dictionary and self._name == other._name

	def __ne__(self, other):
		"""
		:type other: GraphObjStyle
		:rtype: bool
		"""
		return self._dictionary != other._dictionary and self._name == other._name

	@property
	def dictionary(self):
		return self._dictionary.copy()

	def copy(self):
		result = self.__class__(name=self._name)
		result._dictionary = self.dictionary.copy()
		return result

	def update(self, other, inplace=False):
		"""
		:param GraphObjStyle or dict other: another style or dictionary that would update this one
		:param bool inplace: if this object should be updated or a new one created
		:rtype: NoneType or GraphObjStyle
		"""
		if inplace:
			if isinstance(other, GraphObjStyle):
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

	def get(self, item):
		if item in STYLE_RENAME:
			item = STYLE_RENAME[item]
		return self.dictionary[item]

	@property
	def colour(self):
		return self.get(item='colour')

	def get_graphviz_str(self):
		"""
		:return:
		"""
		key_values = []
		for key, value in self._dictionary.items():
			if isinstance(value, Colour):
				value.use()
				value = value.get_hexadecimal(opacity=self._opacity)

			if isinstance(key, str):
				key = key.strip('"')

			if isinstance(value, str):
				value = value.strip('"')

			if value is not None:
				key_values.append((key, value))

		return ' '.join([f'"{key}"="{value}"' for key, value in key_values])
