

def _get_ancestors(obj, _objects_travelled=None, max_height=None):
	"""
	:type _objects_travelled: list or NoneType
	:rtype: list[Node]
	"""
	if max_height is not None:
		if max_height <= 0:
			return [], {}
		else:
			max_height -= 1
	_objects_travelled = _objects_travelled or []
	_objects_travelled.append(obj)
	parents = obj.__parents__()
	if len(parents) == 0:
		return [], {}
	else:
		ancestors = []
		ancestors_dict = {1: []}
		for parent in parents:
			if parent not in _objects_travelled:
				if parent not in ancestors:
					ancestors.append(parent)
					ancestors_dict[1].append(parent)
				parent_ancestors, parent_ancestors_dict = _get_ancestors(
					obj=parent, _objects_travelled=_objects_travelled, max_height=max_height
				)
				for ancestor in parent_ancestors:
					if ancestor not in ancestors:
						ancestors.append(ancestor)
						for distance in parent_ancestors_dict.keys():
							ancestors_dict[distance + 1] = parent_ancestors_dict[distance]
		return ancestors, ancestors_dict


def get_ancestors(obj, distance=True, max_height=None):
	ancestors, ancestors_dict = _get_ancestors(obj=obj, _objects_travelled=None, max_height=max_height)
	if distance:
		return ancestors_dict
	else:
		return ancestors
