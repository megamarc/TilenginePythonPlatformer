""" Flying enemy, waves across screen """

from math import sin, radians
from tilengine import Spriteset, Sequence, Flags
from actor import Actor, Direction
import game

class Eagle(Actor):
	""" Flying enemy """
	size = (40, 40)
	seq_fly = None

	def __init__(self, item_ref, x, y):
		
		# init class members once
		if Eagle.spriteset is None:
			Eagle.spriteset = Spriteset.fromfile("enemy_eagle")
			Eagle.seq_fly = Sequence.create_sprite_sequence(Eagle.spriteset, "fly", 6)

		Actor.__init__(self, item_ref, x, y)
		self.frame = 0
		self.base_y = y
		self.xspeed = -3
		self.direction = Direction.Left
		self.sprite.set_animation(Eagle.seq_fly, 0)
		self.collision_points = (4, 20, 36)

	def update(self):
		""" Update once per frame """
		self.x += self.xspeed
		self.y = self.base_y + int(sin(radians(self.frame*4))*15)
		self.frame += 1
		if self.frame is 10:
			game.sounds.play("eagle", 3)
		screen_x = self.x - game.world.x

		if self.direction is Direction.Left:
			if screen_x < 10:
				self.direction = Direction.Right
				self.xspeed = -self.xspeed
				self.sprite.set_flags(Flags.FLIPX)
				game.sounds.play("eagle", 3)
			else:
				for point in self.collision_points:
					game.player.check_hit(self.x, self.y + point, self.direction)
		else:
			if screen_x > 590:
				self.direction = Direction.Left
				self.xspeed = -self.xspeed
				self.sprite.set_flags(0)
				game.sounds.play("eagle", 3)
			else:
				for point in self.collision_points:
					game.player.check_hit(self.x + self.size[0], self.y + point, self.direction)
		self.sprite.set_position(screen_x, self.y)
		return True
