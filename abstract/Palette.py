import colorsys


def rgb_to_hex(r, g, b):
	r = int(min(max(0, r*256 - 1), 255))
	g = int(min(max(0, g*256 - 1), 255))
	b = int(min(max(0, b*256 - 1), 255))
	return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Palette:
	def __init__(self, hue, saturation, luminosity, num_levels):
		self._hue = hue
		self._saturation = saturation
		self._luminosity = luminosity
		self._num_levels = num_levels

	@property
	def num_levels(self):
		return self._num_levels

	@property
	def hue_step(self):
		return (self._hue[1] - self._hue[0]) / self._num_levels

	@property
	def saturation_step(self):
		return (self._saturation[1] - self._saturation[0]) / self._num_levels

	@property
	def luminosity_step(self):
		return (self._luminosity[1] - self._luminosity[0]) / self._num_levels

	@property
	def hls_values(self):
		return [
			(
				self._hue[0] + self.hue_step*i,
				self._luminosity[0] + self.luminosity_step*i,
				self._saturation[0] + self.saturation_step*i
			)
			for i in range(self._num_levels)
		]

	def get_hex(self, index, h=None, l=None, s=None):
		r, g, b = self.get_rgb(index=index, h=h, l=l, s=s)
		return rgb_to_hex(r=r, g=g, b=b)

	def get_rgb(self, index, h=None, l=None, s=None):
		hls = self.hls_values[index % len(self.hls_values)]
		h = h or hls[0]
		l = l or hls[1]
		s = s or hls[2]
		return colorsys.hls_to_rgb(h=h, l=l, s=s)

	@property
	def rgb_values(self):
		return [
			colorsys.hls_to_rgb(h=h, l=l, s=s)
			for h, l, s in self.hls_values
		]

	@property
	def hex_values(self):
		return [rgb_to_hex(r=r, g=g, b=b) for r, g, b in self.rgb_values]

	def __str__(self):
		return ', '.join(self.hex_values)

	def __repr__(self):
		return str(self)
