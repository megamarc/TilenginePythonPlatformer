""" UI HUD elements (time, score...) """

from tilengine import Tileset, Tilemap, Tile
import game

class UI(object):
	""" UI elements """
	def __init__(self):
		self.cols = game.WIDTH//8
		self.layer = game.engine.layers[0]
		self.layer.setup(Tilemap.create(4, self.cols, None), Tileset.fromfile("ui.tsx"))
		self.layer.set_clip(0, 0, game.WIDTH, 32)

	def update_time(self, time):
		text = "{:03}".format(time)
		col = (self.cols - len(text)) // 2
		tile = Tile()
		for digit in text:
			base_index = int(digit)
			tile.index = base_index + 11
			self.layer.tilemap.set_tile(1, col, tile)
			tile.index = base_index + 21
			self.layer.tilemap.set_tile(2, col, tile)
			col += 1
