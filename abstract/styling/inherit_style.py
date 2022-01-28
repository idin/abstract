from colouration import Colour
from .is_root_or_parents_are_in_loop import is_root_or_parents_are_in_loop


def generate_diverging_numbers(n):
	if n == 1:
		return [0]
	elif n % 2 == 0:
		return [x/(n/2) for x in range(1, n // 2 + 1)] + [-x/(n/2) for x in range(1, n // 2 + 1)]
	else:
		return [0] + generate_diverging_numbers(n-1)


def get_diverging_number(i, n, reverse):
	return sorted(generate_diverging_numbers(n), reverse=reverse)[i]


def inherit_style(node, pale_ratio, divergence_ratio, main_style):
	"""
	:type node: Node
	:rtype: NodeStyle
	"""
	if is_root_or_parents_are_in_loop(node):
		if main_style is None:
			return node.style.copy()
		else:
			return main_style.copy()
	else:
		if len(node.parents) == 1:
			parent = node.parents[0]
			num_siblings = len(parent.children)
			rank = node.get_child_rank(parent=parent)
			if main_style is None:
				style = inherit_style(
					node=parent, pale_ratio=pale_ratio, divergence_ratio=divergence_ratio, main_style=main_style
				)
			else:
				style = main_style
			if num_siblings == 0:
				colour = style.colour.copy(keep_id=True)
			else:
				colour = style.colour.increase_hue(
					amount=divergence_ratio * get_diverging_number(i=rank, n=num_siblings, reverse=False)
				)
			#colour = colour.pale(ratio=pale_ratio)
			colour.saturation = colour.saturation * 3 / 4
			new_style = style.copy()
			new_style.reset_colours()
			new_style.colour = colour
			return new_style
		else:
			styles = [
				inherit_style(node=parent, pale_ratio=pale_ratio, divergence_ratio=0, main_style=main_style)
				for parent in node.parents
				if not node.is_in_loop_with(parent)
			]
			colours = [style.colour for style in styles]
			if main_style is None:
				style = styles[0]
			else:
				style = main_style
			colour = Colour.mix(colours=colours).pale(ratio=pale_ratio)
			new_style = style.copy()
			new_style.reset_colours()
			new_style.colour = colour
			return new_style
