import hashlib
import base32hex


def make_hash_sha256(obj):
	hasher = hashlib.sha256()
	hasher.update(repr(obj).encode())
	return base32hex.b32encode(hasher.digest()).replace('=', '-')


class GraphObj:
	def __init__(self, graph, id, value=None, label=None, style=None, **kwargs):
		self._graph = graph
		self._raw_id = id
		self._value = value
		self._label = label
		self._style = None
		self._frozen = False
		self._parameters = dict(kwargs)
		self.style = style

	def __getstate__(self):
		return {
			'graph': None,
			'id': self.raw_id,
			'value': self._value,
			'label': self._label,
			'style': self._style,
			'frozen': self._frozen,
			'parameters': self._parameters
		}

	def __setstate__(self, state):
		self._graph = state['graph']
		self._raw_id = state['id']
		self._value = state['value']
		self._label = state['label']
		self._style = state['style']
		self._frozen = state['frozen']
		self._parameters = state['parameters']

	def get(self, item):
		return self._parameters[item]

	def set(self, item, value):
		self._parameters[item] = value

	def __getitem__(self, item):
		return self.get(item=item)

	def __setitem__(self, key, value):
		self.set(item=key, value=value)

	@property
	def graph(self):
		return self._graph

	@property
	def id(self):
		return self.raw_id

	@property
	def raw_id(self):
		return self._raw_id

	@raw_id.setter
	def raw_id(self, raw_id):
		self._raw_id = raw_id

	def __hash__(self):
		return make_hash_sha256((self._graph.__hash__(), self.id)).__hash__()

	@property
	def is_frozen(self):
		return self._frozen

	def freeze(self):
		self._frozen = True

	def unfreeze(self):
		self._frozen = False

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, value):
		if self.is_frozen:
			raise RuntimeError('GraphObj is frozen!')
		self._value = value

	@property
	def raw_label(self):
		return self._label

	@property
	def label(self):
		return self.raw_label

	@label.setter
	def label(self, label):
		self._label = label

	@property
	def label_or_value(self):
		if self._label is not None:
			return self._label
		else:
			return self._value

	def __eq__(self, other):
		"""
		:type other: GraphObj
		:rtype: bool
		"""
		if not isinstance(other, self.__class__):
			raise TypeError(f'"{other}" is of type: {type(other)}')
		if self.graph != other.graph:
			raise ValueError('two GraphObj from different graphs cannot be compared')
		return self.id == other.id

	def __ne__(self, other):
		"""
		:type other: GraphObj
		:rtype: bool
		"""
		if not isinstance(other, self.__class__):
			raise TypeError(f'"{other}" is of type: {type(other)}')
		if self.graph != other.graph:
			raise ValueError('two GraphObj from different graphs cannot be compared')
		return self.raw_id != other.raw_id

	def is_similar_to(self, other):
		"""
		:type other: GraphObj
		:rtype: bool
		"""
		return self.id == other.id and self._value == other._value and self._style == other._style and self._parameters == other._parameters
