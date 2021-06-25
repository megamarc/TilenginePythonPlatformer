""" Main player game entity """

from tilengine import Spriteset, Sequence, Palette, Input, Flags, TileInfo
from actor import Actor, Direction
from world import Medium, Tiles
from eagle import Eagle
from opossum import Opossum
from rectangle import Rectangle
from effect import Effect
from score import Score
import game

tiles_info = (TileInfo(), TileInfo(), TileInfo(), TileInfo())

class State:
	""" player states """
	Undefined, Idle, Run, Jump, Hit = range(5)


class Player(Actor):
	""" main player entity """
	size = (24, 36)
	xspeed_delta = 12
	xspeed_limit = 200
	yspeed_delta = 10
	yspeed_limit = 350
	jspeed_delta = 5

	seq_idle = None
	seq_jump = None
	seq_run = None
	spriteset_death = None
	seq_death = None

	def __init__(self):
		
		# init class members once
		if Player.spriteset is None:
			Player.spriteset = Spriteset.fromfile("hero")
			Player.seq_idle = Sequence.create_sprite_sequence(Player.spriteset, "idle", 4)
			Player.seq_jump = Sequence.create_sprite_sequence(Player.spriteset, "jump", 24)
			Player.seq_run = Sequence.create_sprite_sequence(Player.spriteset, "run", 5)
			Player.spriteset_death = Spriteset.fromfile("effect_death")
			Player.seq_death = Sequence.create_sprite_sequence(Player.spriteset_death, "death-", 5)

		Actor.__init__(self, None, 60, 188)
		self.state = State.Undefined
		self.direction = Direction.Right
		self.xspeed = 0
		self.yspeed = 0
		self.set_idle()
		self.sprite.set_position(self.x, self.y)
		self.width = self.size[0]
		self.height = self.size[1]
		self.medium = Medium.Floor
		self.jump = False
		self.immunity = 0
		self.rectangle = Rectangle(0, 0, self.width, self.height)


		self.palettes = (self.spriteset.palette, Palette.fromfile("hero_alt.act"))

	def set_idle(self):
		""" sets idle state, idempotent """
		if self.state is not State.Idle:
			self.sprite.set_animation(Player.seq_idle, 0)
			self.state = State.Idle
			self.xspeed = 0

	def set_running(self):
		""" sets running state, idempotent """
		if self.state is not State.Run:
			self.sprite.set_animation(Player.seq_run, 0)
			self.state = State.Run

	def set_jump(self):
		""" sets jump state, idempotent """
		if self.state is not State.Jump:
			self.yspeed = -280
			self.sprite.set_animation(Player.seq_jump, 0)
			self.state = State.Jump
			self.medium = Medium.Air
			game.sounds.play("jump", 0)

	def set_bounce(self):
		""" bounces on top of an enemy """
		self.yspeed = -150
		self.state = State.Jump
		self.medium = Medium.Air

	def set_hit(self, enemy_direction):
		""" sets hit animation by an enemy """
		self.direction = enemy_direction
		if self.direction is Direction.Left:
			self.xspeed = -self.xspeed_limit
			self.sprite.set_flags(0)
		else:
			self.xspeed = self.xspeed_limit
			self.sprite.set_flags(Flags.FLIPX)
		self.yspeed = -150
		self.state = State.Hit
		self.medium = Medium.Air
		self.sprite.disable_animation()
		self.sprite.set_picture(12)
		self.immunity = 90
		game.sounds.play("hurt", 0)
		game.world.add_timer(-5)
		Score(-5, self.x, self.y)

	def update_direction(self):
		""" updates sprite facing depending on direction """
		if game.window.get_input(Input.RIGHT):
			direction = Direction.Right
		elif game.window.get_input(Input.LEFT):
			direction = Direction.Left
		else:
			direction = self.direction
		if self.direction is not direction:
			self.direction = direction
			if self.direction is Direction.Right:
				self.sprite.set_flags(0)
			else:
				self.sprite.set_flags(Flags.FLIPX)

	def update_floor(self):
		""" process input when player is in floor medium """
		if game.window.get_input(Input.RIGHT) and self.xspeed < Player.xspeed_limit:
			self.xspeed += self.xspeed_delta
			self.set_running()
		elif game.window.get_input(Input.LEFT) and self.xspeed > -Player.xspeed_limit:
			self.xspeed -= Player.xspeed_delta
			self.set_running()
		elif abs(self.xspeed) < Player.xspeed_delta:
			self.xspeed = 0
		elif self.xspeed > 0:
			self.xspeed -= Player.xspeed_delta
		elif self.xspeed < 0:
			self.xspeed += Player.xspeed_delta
		if self.xspeed == 0:
			self.set_idle()
		if game.window.get_input(Input.A):
			if self.jump is not True:
				self.set_jump()
				self.jump = True
		else:
			self.jump = False

	def update_air(self):
		""" process input when player is in air medium """
		if game.window.get_input(Input.RIGHT) and self.xspeed < Player.xspeed_limit:
			self.xspeed += self.jspeed_delta
		elif game.window.get_input(Input.LEFT) and self.xspeed > -Player.xspeed_limit:
			self.xspeed -= self.jspeed_delta

	def check_left(self, x, y):
		""" checks/adjusts environment collision when player is moving to the left """
		game.world.foreground.get_tile(x, y + 4, tiles_info[0])
		game.world.foreground.get_tile(x, y + 18, tiles_info[1])
		game.world.foreground.get_tile(x, y + 34, tiles_info[2])
		if Tiles.Wall in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.x = (tiles_info[0].col + 1) * 16
			self.xspeed = 0
		game.world.pick_gem(tiles_info)

	def check_right(self, x, y):
		""" checks/adjusts environment collision when player is moving to the right """
		game.world.foreground.get_tile(x + self.width, y + 4, tiles_info[0])
		game.world.foreground.get_tile(x + self.width, y + 18, tiles_info[1])
		game.world.foreground.get_tile(x + self.width, y + 34, tiles_info[2])
		if Tiles.Wall in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.x = (tiles_info[0].col * 16) - self.width
			self.xspeed = 0
		game.world.pick_gem(tiles_info)

	def check_top(self, x, y):
		""" checks/adjusts environment collision when player is jumping """
		game.world.foreground.get_tile(x + 0, y, tiles_info[0])
		game.world.foreground.get_tile(x + 12, y, tiles_info[1])
		game.world.foreground.get_tile(x + 24, y, tiles_info[2])
		if Tiles.Wall in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.y = (tiles_info[0].row + 1) * 16
			self.yspeed = 0
		game.world.pick_gem(tiles_info)

	def check_bottom(self, x, y):
		""" checks/adjusts environment collision when player is falling or running """
		ground = False

		game.world.foreground.get_tile(x + 0, y + self.height, tiles_info[0])
		game.world.foreground.get_tile(x + 12, y + self.height, tiles_info[1])
		game.world.foreground.get_tile(x + 24, y + self.height, tiles_info[2])
		game.world.foreground.get_tile(x + 12, y + self.height - 1, tiles_info[3])

		# check up slope
		if tiles_info[3].type is Tiles.SlopeUp:
			slope_height = 16 - tiles_info[3].xoffset
			if self.yspeed >= 0 and tiles_info[3].yoffset > slope_height:
				self.y -= (tiles_info[3].yoffset - slope_height)
				ground = True

		# check down slope
		elif tiles_info[3].type is Tiles.SlopeDown:
			slope_height = tiles_info[3].xoffset + 1
			if self.yspeed >= 0 and tiles_info[3].yoffset > slope_height:
				self.y -= (tiles_info[3].yoffset - slope_height)
				ground = True

		# check inner slope (avoid falling between staircased slopes)
		elif tiles_info[1].type is Tiles.InnerSlopeUp:
			if self.xspeed > 0:
				self.y = (tiles_info[1].row * 16) - self.height - 1
			else:
				self.x -= 1
			ground = True

		elif tiles_info[1].type is Tiles.InnerSlopeDown:
			if self.xspeed > 0:
				self.x += 1
			else:
				self.y = (tiles_info[1].row * 16) - self.height - 1
			ground = True

		# check regular floor
		elif Tiles.Floor in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.y = (tiles_info[0].row * 16) - self.height
			ground = True

		# adjust to ground
		if ground is True:
			self.yspeed = 0
			if self.medium is Medium.Air:
				self.medium = Medium.Floor
				if self.xspeed == 0:
					self.set_idle()
				else:
					self.set_running()
		else:
			self.medium = Medium.Air
		game.world.pick_gem(tiles_info)

	def check_jump_on_enemies(self, x, y):
		""" checks jumping above an enemy. If so, kills it, bounces and spawns a death animation """
		px, py = x+self.width/2, y+self.height
		for actor in game.actors:
			actor_type = type(actor)
			if actor_type in (Eagle, Opossum):
				ex, ey = actor.x + actor.size[0]/2, actor.y
				if abs(px - ex) < 25 and 5 < py - ey < 20:
					game.world.add_timer(5)
					actor.kill()
					self.set_bounce()
					Effect(actor.x, actor.y - 10, self.spriteset_death, self.seq_death)
					game.sounds.play("crush", 2)
		return

	def check_hit(self, x, y, direction):
		""" returns if get hurt by enemy at select position and direction"""
		if self.immunity is 0 and self.rectangle.check_point(x, y):
			self.set_hit(direction)

	def update(self):
		""" process input and updates state once per frame """
		oldx = self.x
		oldy = self.y

		# update immunity
		if self.immunity is not 0:
			pal_index0 = (self.immunity >> 2) & 1
			self.immunity -= 1
			pal_index1 = (self.immunity >> 2) & 1
			if self.immunity is 0:
				pal_index1 = 0
			if pal_index0 != pal_index1:
				self.sprite.set_palette(self.palettes[pal_index1])

		# update sprite facing
		self.update_direction()

		# user input: move character depending on medium
		if self.medium is Medium.Floor:
			self.update_floor()
		elif self.medium is Medium.Air:
			if self.state is not State.Hit:
				self.update_air()
			if self.yspeed < Player.yspeed_limit:
				self.yspeed += Player.yspeed_delta

		self.x += (self.xspeed / 100.0)
		self.y += (self.yspeed / 100.0)

		# clip to game.world limits
		if self.x < 0.0:
			self.x = 0.0
		elif self.x > game.world.foreground.width - self.width:
			self.x = game.world.foreground.width	- self.width

		# check and fix 4-way collisions depending on motion direction
		intx = int(self.x)
		inty = int(self.y)
		if self.yspeed < 0:
			self.check_top(intx, inty)
		elif self.yspeed >= 0:
			self.check_bottom(intx, inty)
		if self.xspeed < 0:
			self.check_left(intx, inty)
		elif self.xspeed > 0:
			self.check_right(intx, inty)
		if self.yspeed > 0:
			self.check_jump_on_enemies(intx, inty)

		if self.x != oldx or self.y != oldy:
			self.rectangle.update_position(int(self.x), int(self.y))
			self.sprite.set_position(int(self.x) - game.world.x, int(self.y))
		return True
