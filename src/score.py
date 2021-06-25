""" Effect that shows pop-up score on player actions """

from tilengine import Spriteset
from actor import Actor
import game

class Score(Actor):
	def __init__(self, value, x, y):

		# init class members once
		if Score.spriteset is None:
			Score.spriteset = Spriteset.fromfile("score")

		Actor.__init__(self, None, int(x), int(y))
		if value is 5:
			self.sprite.set_picture(0)
		elif value is -5:
			self.sprite.set_picture(1)
		elif value is 1:
			self.sprite.set_picture(2)

		self.t0 = game.window.get_ticks()
		self.t1 = self.t0 + 1000

	def update(self):
		now = game.window.get_ticks()
		p = (now - self.t0) / (self.t1 - self.t0)
		p = -(p * (p - 2))
		self.sprite.set_position(int(self.x - game.world.x), int(self.y - p*16))
		return now < self.t1
