from .NodeStyle import NodeStyle, DEFAULT_FONT, DEFAULT_SHAPE, DEFAULT_SHAPE_STYLE
from colouration import Colour

def generate_diverging_numbers(n):
	if n == 1:
		return [0]
	elif n % 2 == 0:
		return [x/(n/2) for x in range(1, n // 2 + 1)] + [-x/(n/2) for x in range(1, n // 2 + 1)]
	else:
		return [0] + generate_diverging_numbers(n-1)

def get_diverging_number(i, n, reverse):
	return sorted(generate_diverging_numbers(n), reverse=reverse)[i]

def mix_node_style_of_parents(node, font=DEFAULT_FONT, shape=DEFAULT_SHAPE, shape_style=DEFAULT_SHAPE_STYLE):
	"""
	:type node: abstract.Node.Node
	:rtype: NodeStyle
	"""
	scheme = node.graph.colour_scheme
	style = None
	colour = None
	if node.has_parents():
		candidates = []
		for parent in node.parents:
			if not parent.is_in_loop() or not parent.is_style_callable():
				style = parent.compiled_style.copy()
				candidates.append((style, node.get_child_rank(parent=parent), len(parent.children)))

		if len(candidates) > 0:
			colour = Colour.mix(
				colours=[
					style.colour.increase_hue(amount=0.1*get_diverging_number(i=rank, n=num_siblings, reverse=False))
					for style, rank, num_siblings in candidates
				]
			)
			colour = colour.pale(ratio=0.2)
			colour.weight = colour.weight**(0.5)
			#colour = colour.mix_with_gray(gray_weight=2)
			style = NodeStyle(colour=colour, font=font, shape=shape, shape_style=shape_style)

	if style is None or colour is None:
		colour = scheme.least_used_colour
		style = NodeStyle(colour=colour, font=font, shape=shape, shape_style=shape_style)

	return style