

def _get_descendants(obj, _objects_travelled=None, max_depth=None):
	"""
	:type _objects_travelled: list or NoneType
	:rtype: list[Node]
	"""
	if max_depth is not None:
		if max_depth <= 0:
			return [], {}
		else:
			max_depth -= 1
	_objects_travelled = _objects_travelled or []
	_objects_travelled.append(obj)
	children = obj.__children__()
	if len(children) == 0:
		return [], {}
	else:
		descendants = []
		descendants_dict = {1: []}
		for child in children:
			if child not in _objects_travelled:
				if child not in descendants:
					descendants.append(child)
					descendants_dict[1].append(child)
				child_descendants, child_descendants_dict = _get_descendants(
					obj=child, _objects_travelled=_objects_travelled, max_depth=max_depth
				)
				for descendant in child_descendants:
					if descendant not in descendants:
						descendants.append(descendant)
						for distance in child_descendants_dict.keys():
							descendants_dict[distance + 1] = child_descendants_dict[distance]
		return descendants, descendants_dict


def get_descendants(obj, distance=True, max_depth=None):
	descendants, descendants_dict = _get_descendants(obj=obj, _objects_travelled=None, max_depth=max_depth)
	if distance:
		return descendants_dict
	else:
		return descendants
