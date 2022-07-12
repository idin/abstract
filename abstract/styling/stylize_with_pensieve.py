from colouration import Scheme
from .NodeStyle import NodeStyle
from .stylize_edges_based_on_nodes import stylize_edges_based_on_nodes
from .is_root_or_parents_are_in_loop import is_root_or_parents_are_in_loop
from .get_least_used_colour import get_least_used_colour
from .inherit_style import inherit_style
DEFAULT_COLOUR_SCHEME = 'pastel15'


def stylize_with_pensieve(
		graph, node_style=None, edge_style=None, pale_ratio=0.05, divergence_ratio=0.05, edge_darkness_ratio=0.1
):
	if isinstance(graph._colour_scheme, str):
		colour_scheme = Scheme(name=graph._colour_scheme)
	else:
		colour_scheme = graph._colour_scheme
	colours_used = {colour: 0 for colour in colour_scheme.colours}

	# roots or semi-roots
	for node in graph.nodes:
		if node.style is None:
			if is_root_or_parents_are_in_loop(node):
				colour = get_least_used_colour(colours_used)
				if node_style is None:
					style = NodeStyle(colour=colour)
				else:
					style = node_style.copy()
					style.reset_colours()
					style.colour = colour
				node.style = style

	# branch nodes
	for node in graph.nodes:
		if not is_root_or_parents_are_in_loop(node) and not node.is_in_loop():
			if node.style is None:
				node.style = inherit_style(
					node=node, pale_ratio=pale_ratio, divergence_ratio=divergence_ratio, main_style=node_style
				)

	# branch edges
	stylize_edges_based_on_nodes(graph=graph, edge_style=edge_style, edge_darkness_ratio=edge_darkness_ratio)
