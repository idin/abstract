import random
from colouration import Scheme
from .NodeStyle import NodeStyle
from .EdgeStyle import EdgeStyle
from .stylize_edges_based_on_nodes import stylize_edges_based_on_nodes
from .get_least_used_colour import get_least_used_colour
from .inherit_style import inherit_style
DEFAULT_COLOUR_SCHEME = 'pastel15'


def stylize_randomly(
		graph, node_style=None, edge_style=None, pale_ratio=0.05, divergence_ratio=0.05, edge_darkness_ratio=0.1,
		seed=42
):
	if isinstance(graph._colour_scheme, str):
		colour_scheme = Scheme(name=graph._colour_scheme)
	else:
		colour_scheme = graph._colour_scheme
	colours_used = {colour: 0 for colour in colour_scheme.colours}

	nodes = list(graph.nodes)
	random.Random(seed).shuffle(nodes)

	# all nodes
	for node in nodes:
		colour = get_least_used_colour(colours_used)
		if node_style is None:
			style = NodeStyle(colour=colour)
		else:
			style = node_style.copy()
			style.reset_colours()
			style.colour = colour
		node.style = style

	# branch edges
	stylize_edges_based_on_nodes(graph=graph, edge_style=edge_style, edge_darkness_ratio=edge_darkness_ratio)
