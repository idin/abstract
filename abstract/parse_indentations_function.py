import re


def parse_indentations(lines, indent=None):
	"""
	Parse an indented outline into (index, level, content, parent) tuples.
	"""
	regex = re.compile(r'^(?P<indent>(?: {4})*)(?P<name>\S.*)')
	stack = []

	for index, line in enumerate(lines):
		line = line.rstrip('\n')
		if indent is None:
			if line.startswith('\t') or line.startswith(' '):
				indent = re.findall(pattern=r'^[ \t]+', string=line)[0]
		if indent is not None:
			line = line.replace(indent, " " * 4, len(line) - len(line.lstrip(indent)))
		if len(line) > 0:
			match = regex.match(line)
			if not match:
				raise ValueError(
					'Indentation not a multiple of spaces or tabs'.format(line)
				)
			level = len(match.group('indent')) // 4
			if level > len(stack):
				raise ValueError('Indentation too deep: "{0}"'.format(line))
			# stack[level:] = [match.group('name')]
			stack[level:] = [index]
			content = match.group('name')
		else:
			content = ''
		yield index, level, content, (stack[level - 1] if level else None)
