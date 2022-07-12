from .EdgeStyle import EdgeStyle


def stylize_edges_based_on_nodes(graph, edge_style=None, edge_darkness_ratio=0.1):
	for edge in graph.edges:
		if edge.style is None:
			colour = edge.start.style.colour.darken(ratio=edge_darkness_ratio)

			if edge_style is None:
				edge_style = EdgeStyle(colour=colour)
			else:
				edge_style = edge_style.copy()
				edge_style.reset_colours()
				edge_style.colour = colour

			if edge.value is not None:
				edge_style._arrow_size *= edge.value

			edge.style = edge_style