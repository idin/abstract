from typing import List, Dict, Optional, Tuple, Union

def _get_descendants(obj, _objects_travelled: Optional[List] = None, max_depth: Optional[int] = None) -> Tuple[List, Dict]:
	"""
	Retrieves the descendants of an object.

	Args:
		obj: The object to retrieve descendants from.
		_objects_travelled (Optional[List]): List of objects already travelled.
		max_depth (Optional[int]): Maximum depth for travelling through objects' children.

	Returns:
		Tuple[List, Dict]: A tuple containing a list of descendants and a dictionary of descendants with their distances.
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


def get_descendants(obj, distance: bool = True, max_depth: Optional[int] = None) -> Union[List, Dict]:
	"""
	Retrieves the descendants of an object.

	Args:
		obj: The object to retrieve descendants from.
		distance (bool): If True, returns descendants with their respective distances.
		max_depth (Optional[int]): Maximum depth for travelling through objects' children.

	Returns:
		Union[List, Dict]: A list of descendants or a dictionary of descendants with their distances.
	"""
	descendants, descendants_dict = _get_descendants(obj=obj, _objects_travelled=None, max_depth=max_depth)
	if distance:
		return descendants_dict
	else:
		return descendants
