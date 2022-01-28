def is_root_or_parents_are_in_loop(node):
	"""
	:type node: Node
	:rtype: bool
	"""
	parents = [parent for parent in node.parents if not parent.is_in_loop()]
	return len(parents) == 0