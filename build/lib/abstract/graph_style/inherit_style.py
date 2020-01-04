from .NodeStyle import NodeStyle
from .EdgeStyle import EdgeStyle, DEFAULT_FONT


def inherit_node_style_from_parent(node):
	"""
	:type node: abstract.Node.Node
	:rtype: NodeStyle
	"""
	scheme = node.graph.colour_scheme
	style = None
	colour = None

	if node.has_parents():
		best_candidates = []
		for parent in node.parents:
			if not parent.is_in_loop() or not parent.is_style_callable():
				style = parent.compiled_style.copy()
				best_candidates.append(style)

		if len(best_candidates) > 0:
			best_candidates.sort(key=lambda x: x.colour.usage_amount)
			style = best_candidates[0]
			colour = style.colour

	if style is None or colour is None:
		colour = scheme.least_used_colour
		style = NodeStyle(colour=colour)

	return style


def inherit_node_style_from_child(node):
	"""
	:type node: abstract.Node.Node
	:rtype: NodeStyle
	"""
	scheme = node.graph.colour_scheme
	style = None
	colour = None
	if node.has_children():
		best_candidates = []
		for child in node.children:
			if not child.is_in_loop() or not child.is_style_callable():
				style = child.compiled_style.copy()
				best_candidates.append(style)
		if len(best_candidates) > 0:
			best_candidates.sort(key=lambda x: x.colour.usage_amount)
			style = best_candidates[0]
			colour = style.colour

	if style is None or colour is None:
		colour = scheme.least_used_colour
		style = NodeStyle(colour=colour)

	return style


def inherit_edge_style_from_start(edge, font=DEFAULT_FONT):
	"""
	:type edge: abstract.Edge.Edge
	:rtype: EdgeStyle
	"""
	colour = edge.start.compiled_style.border_colour
	return EdgeStyle(colour=colour, font=font)


def inherit_edge_style_from_end(edge, font=DEFAULT_FONT):
	"""
	:type edge: abstract.Edge.Edge
	:rtype: EdgeStyle
	"""
	colour = edge.end.compiled_style.border_colour
	return EdgeStyle(colour=colour, font=font)





