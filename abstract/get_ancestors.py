from typing import List, Dict, Optional, Tuple, Union

def _get_ancestors(obj, _objects_travelled: Optional[List] = None, max_height: Optional[int] = None) -> Tuple[List, Dict]:
	"""
	Retrieves the ancestors of an object.

	Args:
		obj: The object to retrieve ancestors from.
		_objects_travelled (Optional[List]): List of objects already travelled.
		max_height (Optional[int]): Maximum height for travelling through objects' parents.

	Returns:
		Tuple[List, Dict]: A tuple containing a list of ancestors and a dictionary of ancestors with their distances.
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


def get_ancestors(obj, distance: bool = True, max_height: Optional[int] = None) -> Union[List, Dict]:
	"""
	Retrieves the ancestors of an object.

	Args:
		obj: The object to retrieve ancestors from.
		distance (bool): If True, returns ancestors with their respective distances.
		max_height (Optional[int]): Maximum height for travelling through objects' parents.

	Returns:
		Union[List, Dict]: A list of ancestors or a dictionary of ancestors with their distances.
	"""
	ancestors, ancestors_dict = _get_ancestors(obj=obj, _objects_travelled=None, max_height=max_height)
	if distance:
		return ancestors_dict
	else:
		return ancestors
