""" Base class for all game entities (actors) """

import game

class Direction:
	""" player orientations """
	Right, Left = range(2)

class Actor(object):
	""" Generic active game entity base class """
	spriteset = None
	def __init__(self, item_ref, x, y):
		self.x = x
		self.y = y
		self.sprite = game.engine.sprites[game.engine.get_available_sprite()]
		self.sprite.setup(self.spriteset)
		self.item = item_ref
		game.actors.append(self)

	def __del__(self):
		self.sprite.disable()
		if self.item is not None:
			self.item.alive = False

	def kill(self):
		""" definitive kill of active game entity, removing from spawn-able item list too """
		game.world.objects.remove(self.item)
		self.item = None
		game.actors.remove(self)
