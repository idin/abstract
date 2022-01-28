def get_least_used_colour(colours_used):
	colour = min(colours_used, key=colours_used.get)
	colours_used[colour] += 1
	return colour
