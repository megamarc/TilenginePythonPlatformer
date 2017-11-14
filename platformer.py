""" Tilengine python platformer demo """
# pylint: disable=C0103
# pylint: disable=W0614
# pylint: disable=W0312
import xml.etree.ElementTree as ET
from math import sin, radians
from tilengine import *

# constants
WIDTH = 640
HEIGHT = 360
sky_color1 = Color(120, 215, 242)
sky_color2 = Color(226, 236, 242)

def load_objects(file_name, layer_name, first_gid):
	""" loads tiles in object layer from a tmx file.
	Returns list of Item objects """
	tree = ET.parse(file_name)
	root = tree.getroot()
	for child in root.findall("objectgroup"):
		name = child.get("name")
		if name == layer_name:
			item_list = list()
			for item in child.findall("object"):
				gid = item.get("gid")
				if gid is not None:
					x = item.get("x")
					y = item.get("y")
					item_list.append(Item(int(gid) - first_gid, int(x), int(y)))
			return item_list
	return None

# Game management definitions *************************************************

class State(object):
	""" player states """
	Undefined, Idle, Run, Jump = range(4)

class Direction(object):
	""" player orientations """
	Right, Left = range(2)

class Tiles(object):
	""" types of tiles for sprite-terrain collision detection """
	Empty, Floor, Gem, Wall, SlopeUp, SlopeDown, InnerSlopeUp, InnerSlopeDown = range(8)

class Medium(object):
	""" types of environments """
	Floor, Air, Ladder, Water = range(4)

class Item(object):
	Opossum, Eagle, Frog = range(3)
	def __init__(self, item_type, x, y):
		self.type = item_type
		self.x = x
		self.y = y
		self.alive = False

	def try_spawn(self, x):
		if self.alive is False and x < self.x < x + WIDTH:
			self.alive = True
			if self.type is Item.Eagle:
				Eagle(self, self.x, self.y)

class Actor(object):
	""" generic game entity base class """
	def __init__(self, item_ref, x, y):
		self.x = x
		self.y = y
		self.sprite = engine.sprites[engine.get_available_sprite()]
		self.animation = engine.animations[engine.get_available_animation()]
		self.item = item_ref
		actors.append(self)

	def __del__(self):
		self.animation.disable()
		self.sprite.disable()
		if self.item is not None:
			world.objects.remove(self.item)

class Player(Actor):
	""" main player entity """
	xspeed_delta = 12
	xspeed_limit = 200
	yspeed_delta = 10
	yspeed_limit = 280
	jspeed_delta = 5
	def __init__(self):
		Actor.__init__(self, None, 60, 188)
		self.state = State.Undefined
		self.direction = Direction.Right
		self.xspeed = 0
		self.yspeed = 0
		self.sprite.setup(Spriteset.fromfile("hero"))
		self.set_idle()
		sprite_info = SpriteInfo()
		self.sprite.spriteset.get_sprite_info(0, sprite_info)
		self.sprite.set_position(self.x, self.y)
		self.width = sprite_info.w
		self.height = sprite_info.h
		self.medium = Medium.Floor
		self.jump = False
		del sprite_info

	def set_idle(self):
		""" sets idle state, idempotent """
		if self.state is not State.Idle:
			self.animation.set_sprite_animation(self.sprite.index, sequence_idle, 0)
			self.state = State.Idle
			self.xspeed = 0

	def set_running(self):
		""" sets running state, idempotent """
		if self.state is not State.Run:
			self.animation.set_sprite_animation(self.sprite.index, sequence_run, 0)
			self.state = State.Run

	def set_jump(self):
		""" sets jump state, idempotent """
		if self.state is not State.Jump:
			self.yspeed = -Player.yspeed_limit
			self.animation.set_sprite_animation(self.sprite.index, sequence_jump, 0)
			self.state = State.Jump
			self.medium = Medium.Air

	def update_direction(self):
		""" updates sprite facing depending on direction """
		if window.get_input(Input.RIGHT):
			direction = Direction.Right
		elif window.get_input(Input.LEFT):
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
		if window.get_input(Input.RIGHT) and self.xspeed < Player.xspeed_limit:
			self.xspeed += self.xspeed_delta
			self.set_running()
		elif window.get_input(Input.LEFT) and self.xspeed > -Player.xspeed_limit:
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
		if window.get_input(Input.A):
			if self.jump is not True:
				player.set_jump()
				self.jump = True
		else:
			self.jump = False

	def update_air(self):
		""" process input when player is in air medium """
		if window.get_input(Input.RIGHT) and self.xspeed < Player.xspeed_limit:
			self.xspeed += self.jspeed_delta
		elif window.get_input(Input.LEFT) and self.xspeed > -Player.xspeed_limit:
			self.xspeed -= self.jspeed_delta
		if self.yspeed < Player.yspeed_limit:
			self.yspeed += Player.yspeed_delta

	def check_left(self, x, y):
		""" checks/adjusts environment collision when player is moving to the left """
		world.foreground.get_tile(x, y + 4, tiles_info[0])
		world.foreground.get_tile(x, y + 18, tiles_info[1])
		world.foreground.get_tile(x, y + 34, tiles_info[2])
		if Tiles.Wall in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.x = (tiles_info[0].col + 1) * 16
			self.xspeed = 0
		world.pick_gem(tiles_info)

	def check_right(self, x, y):
		""" checks/adjusts environment collision when player is moving to the right """
		world.foreground.get_tile(x + self.width, y + 4, tiles_info[0])
		world.foreground.get_tile(x + self.width, y + 18, tiles_info[1])
		world.foreground.get_tile(x + self.width, y + 34, tiles_info[2])
		if Tiles.Wall in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.x = (tiles_info[0].col * 16) - self.width
			self.xspeed = 0
		world.pick_gem(tiles_info)

	def check_top(self, x, y):
		""" checks/adjusts environment collision when player is jumping """
		world.foreground.get_tile(x + 0, y, tiles_info[0])
		world.foreground.get_tile(x + 12, y, tiles_info[1])
		world.foreground.get_tile(x + 24, y, tiles_info[2])
		if Tiles.Wall in (tiles_info[0].type, tiles_info[1].type, tiles_info[2].type):
			self.y = (tiles_info[0].row + 1) * 16
			self.yspeed = 0
		world.pick_gem(tiles_info)

	def check_bottom(self, x, y):
		""" checks/adjusts environment collision when player is falling or running """
		ground = False

		world.foreground.get_tile(x + 0, y + self.height, tiles_info[0])
		world.foreground.get_tile(x + 12, y + self.height, tiles_info[1])
		world.foreground.get_tile(x + 24, y + self.height, tiles_info[2])
		world.foreground.get_tile(x + 12, y + self.height - 1, tiles_info[3])

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
			self.yspeed += Player.yspeed_delta
			if self.medium is Medium.Floor:
				self.medium = Medium.Air
		world.pick_gem(tiles_info)

	def update(self):
		""" process input and updates state once per frame """
		oldx = self.x
		oldy = self.y

		# update sprite facing
		self.update_direction()

		# user input: move character depending on medium
		if self.medium is Medium.Floor:
			self.update_floor()
		elif self.medium is Medium.Air:
			self.update_air()

		self.x += (self.xspeed / 100.0)
		self.y += (self.yspeed / 100.0)

		# clip to world limits
		if self.x < 0.0:
			self.x = 0.0
		elif self.x > world.foreground.width - self.width:
			self.x = world.foreground.width	- self.width

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

		if self.x is not oldx or self.y is not oldy:
			self.sprite.set_position(int(self.x) - world.x, int(self.y))
		return True


class Eagle(Actor):
	""" Flying enemy """
	spriteset = None
	def __init__(self, item_ref, x, y):
		if Eagle.spriteset is None:
			Eagle.spriteset = Spriteset.fromfile("eagle")

		Actor.__init__(self, item_ref, x, y)
		self.frame = 0
		self.base_y = y
		self.sprite.setup(Eagle.spriteset)
		self.animation.set_sprite_animation(self.sprite.index, sequence_eagle, 0)

	def update(self):
		""" Update once per frame """
		self.x -= 3
		self.y = self.base_y + int(sin(radians(self.frame*4))*15)
		self.frame += 1
		self.sprite.set_position(self.x - world.x, self.y)
		if self.x + 40 < world.x:
			return False
		return True

class World(object):
	""" world/play field entity """
	def __init__(self):
		self.foreground = engine.layers[0]
		self.background = engine.layers[1]
		self.clouds = 0.0
		self.foreground.setup(Tilemap.fromfile("layer_foreground.tmx"))
		self.background.setup(Tilemap.fromfile("layer_background.tmx"))
		self.x = 0
		self.x_max = self.foreground.width - WIDTH
		self.objects = load_objects("layer_foreground.tmx", "Capa de Objetos 1", 973)
		engine.set_background_color(self.background.tilemap)
		actors.append(self)

	def pick_gem(self, tiles_list):
		""" updates tilemap when player picks a gem """
		tile = Tile()
		tile.index = 0
		for tile_info in tiles_list:
			if tile_info.type is Tiles.Gem:
				self.foreground.tilemap.set_tile(tile_info.row, tile_info.col, tile)
				Effect(tile_info.col*16, tile_info.row*16, sequence_vanish)
				break
		del tile

	def update(self):
		""" updates world state once per frame """
		oldx = self.x

		if player.x < 240:
			self.x = 0
		else:
			self.x = int(player.x - 240)
		if self.x > self.x_max:
			self.x = self.x_max
		self.clouds += 0.1

		if self.x is not oldx:
			self.foreground.set_position(self.x, 0)
			self.background.set_position(self.x/8, 0)

		# spawn new entities from object list
		for item in self.objects:
			item.try_spawn(self.x)

		return True

class Effect(Actor):
	""" placeholder for simple sprite effects """
	spriteset = None
	def __init__(self, x, y, sequence):
		if Effect.spriteset is None:
			Effect.spriteset = Spriteset.fromfile("effects")
		Actor.__init__(self, None, x, y)
		self.sprite.setup(Effect.spriteset)
		self.sprite.set_position(x, y)
		self.animation.set_sprite_animation(self.sprite.index, sequence, 1)

	def update(self):
		""" updates effect state once per frame """
		self.sprite.set_position(self.x - world.x, self.y)
		if self.animation.get_state() is False:
			return False
		return True

# Raster effect related functions *********************************************

def lerp(pos_x, x0, x1, fx0, fx1):
	""" integer linear interpolation """
	return fx0 + (fx1 - fx0) * (pos_x - x0) // (x1 - x0)

def interpolate_color(x, x1, x2, color1, color2):
	""" linear interpolation between two Color objects """
	r = lerp(x, x1, x2, color1.r, color2.r)
	g = lerp(x, x1, x2, color1.g, color2.g)
	b = lerp(x, x1, x2, color1.b, color2.b)
	return Color(r, g, b)

def raster_effect(line):
	""" raster effect callback, called every rendered scanline """
	if 0 <= line <= 128:
		color = interpolate_color(line, 0, 128, sky_color1, sky_color2)
		engine.set_background_color(color)

	if line == 0:
		world.background.set_position(int(world.clouds), 0)

	elif 160 <= line <= 208:
		pos1 = world.x//10
		pos2 = world.x//3
		xpos = lerp(line, 160, 208, pos1, pos2)
		world.background.set_position(xpos, 0)

	elif line == 256:
		world.background.set_position(world.x//2, 0)

# init engine
engine = Engine.create(WIDTH, HEIGHT, 2, 16, 16)

# load sequences for player character
sequences = SequencePack.fromfile("hero.sqx")
sequence_idle = sequences.find_sequence("seq_idle")
sequence_jump = sequences.find_sequence("seq_jump")
sequence_run = sequences.find_sequence("seq_run")
sequence_vanish = sequences.find_sequence("seq_vanish")
sequence_eagle = sequences.find_sequence("seq_eagle")
tiles_info = [TileInfo(), TileInfo(), TileInfo(), TileInfo()]

# set raster callback
engine.set_raster_callback(raster_effect)

actors = list()		# this list contains every active game entity
world = World()		# world/level entity
player = Player()   # player entity

# window creation & main loop
window = Window.create()
while window.process():

	# update active entities list
	for actor in actors:
		if not actor.update():
			actors.remove(actor)

engine.delete()
