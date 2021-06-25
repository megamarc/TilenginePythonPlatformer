""" Terrestrial enemy, chases player on floor """

from tilengine import Spriteset, Sequence, Flags
from actor import Actor, Direction
import game

class Opossum(Actor):
	""" Floor enemy. Chases player in a 80 pixel radius """
	size = (36, 24)
	seq_walk = None

	def __init__(self, item_ref, x, y):

		# init class members once
		if Opossum.spriteset is None:
			Opossum.spriteset = Spriteset.fromfile("enemy_opossum")
			Opossum.seq_walk = Sequence.create_sprite_sequence(Opossum.spriteset, "opossum-", 6)

		Actor.__init__(self, item_ref, x, y)
		self.xspeed = -2
		self.direction = Direction.Left
		self.sprite.set_animation(Opossum.seq_walk, 0)

	def update(self):
		""" Update once per frame """
		self.x += self.xspeed
		if self.direction is Direction.Left:
			if self.x - game.player.x < -80:
				self.direction = Direction.Right
				self.xspeed = -self.xspeed
				self.sprite.set_flags(Flags.FLIPX)
			else:
				game.player.check_hit(self.x, self.y + self.size[1]//2, self.direction)
		else:
			if self.x - game.player.x > 80 and self.direction is Direction.Right:
				self.direction = Direction.Left
				self.xspeed = -self.xspeed
				self.sprite.set_flags(0)
			else:
				game.player.check_hit(self.x + self.size[0], self.y + self.size[1]//2, self.direction)

		self.sprite.set_position(self.x - game.world.x, self.y)
		return True
