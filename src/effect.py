""" Generic, reusable one-shot animation (explosions, vanish, smoke...) """

from actor import Actor
import game

class Effect(Actor):
	""" placeholder for simple sprite effects """
	def __init__(self, x, y, spriteset, sequence):
		self.spriteset = spriteset
		Actor.__init__(self, None, x, y)
		self.sprite.set_animation(sequence, 1)

	def update(self):
		""" updates effect state once per frame """
		self.sprite.set_position(self.x - game.world.x, self.y)
		if self.sprite.get_animation_state() is False:
			return False
		return True
