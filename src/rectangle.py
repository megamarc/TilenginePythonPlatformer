""" Basic rectangle helper for hitboxes """

class Rectangle(object):
	""" aux rectangle """
	def __init__(self, x, y, w, h):
		self.width = w
		self.height = h
		self.update_position(x, y)

	def update_position(self, x, y):
		self.x1 = x
		self.y1 = y
		self.x2 = x + self.width
		self.y2 = y + self.height

	def check_point(self, x, y):
		""" returns if point is contained in rectangle """
		return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
