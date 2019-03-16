import hashlib
import base32hex

def make_hash_sha256(obj):
	hasher = hashlib.sha256()
	hasher.update(repr(obj).encode())
	return base32hex.b32encode(hasher.digest()).replace('=', '-')

class GraphObj:
	def __init__(self, graph, id, value=None, label=None, style=None, **kwargs):
		self._graph = graph
		self._id = id
		self._value = value
		self._label = label
		self._style = style
		self._frozen = False
		self._parameters = dict(kwargs)

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
		return self._id

	def __hash__(self):
		return make_hash_sha256((self._graph.__hash__(), self.id))

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
	def label(self):
		return self._label

	@label.setter
	def label(self, label):
		self._label = label

	@property
	def label_or_value(self):
		if self._label is not None:
			return self._label
		else:
			return self._value

	@property
	def style(self):
		return self._style

	@style.setter
	def style(self, style):
		self._style = style

	def __eq__(self, other):
		"""
		:type other: GraphObj
		:rtype: bool
		"""
		if not isinstance(other, self.__class__): raise TypeError(f'"{other}" is of type: {type(other)}')
		if self.graph != other.graph: raise ValueError('two GraphObj from different graphs cannot be compared')
		return self.id == other.id

	def __ne__(self, other):
		"""
		:type other: GraphObj
		:rtype: bool
		"""
		if not isinstance(other, self.__class__): raise TypeError(f'"{other}" is of type: {type(other)}')
		if self.graph != other.graph: raise ValueError('two GraphObj from different graphs cannot be compared')
		return self._id != other._id


