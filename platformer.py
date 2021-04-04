""" Tilengine python platformer demo """
# pylint: disable=C0103
# pylint: disable=W0614
# pylint: disable=W0312
import xml.etree.ElementTree as ET
from math import sin, radians
from tilengine import *
from sound import Sound

# constants
WIDTH = 640
HEIGHT = 360
ASSETS_PATH = "assets"
SKY_COLORS = (Color.fromstring("#78D7F2"), Color.fromstring("#E2ECF2"))

# init engine
engine = Engine.create(WIDTH, HEIGHT, 3, 32, 0)
engine.set_load_path("assets")

# load spritesets for animation effects
spriteset_vanish = Spriteset.fromfile("effect_vanish")
spriteset_death = Spriteset.fromfile("effect_death")

# create sequences
seq_vanish = Sequence.create_sprite_sequence(spriteset_vanish, "vanish", 4)
seq_death = Sequence.create_sprite_sequence(spriteset_death, "death-", 5)

tiles_info = (TileInfo(), TileInfo(), TileInfo(), TileInfo())

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

class State:
	""" player states """
	Undefined, Idle, Run, Jump, Hit = range(5)

class Direction:
	""" player orientations """
	Right, Left = range(2)

class Tiles:
	""" types of tiles for sprite-terrain collision detection """
	Empty, Floor, Gem, Wall, SlopeUp, SlopeDown, InnerSlopeUp, InnerSlopeDown = range(8)

class Medium:
	""" types of environments """
	Floor, Air, Ladder, Water = range(4)

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

class Item(object):
	""" Generic item declared in tilemap object layer awaiting to spawn """
	Opossum, Eagle, Frog = range(3)
	def __init__(self, item_type, x, y):
		self.type = item_type
		self.x = x
		self.y = y
		self.alive = False

	def try_spawn(self, x):
		""" Tries to spawn an active game object depending on screen position and item type """
		if self.alive is False and x < self.x < x + WIDTH:
			self.alive = True
			if self.type is Item.Eagle:
				Eagle(self, self.x, self.y - Eagle.size[1])
			elif self.type is Item.Opossum:
				Opossum(self, self.x, self.y - Opossum.size[1])

class Actor(object):
	""" Generic active game entity base class """
	spriteset = None
	def __init__(self, item_ref, x, y):
		self.x = x
		self.y = y
		self.sprite = engine.sprites[engine.get_available_sprite()]
		self.sprite.setup(self.spriteset)
		self.item = item_ref
		actors.append(self)

	def __del__(self):
		self.sprite.disable()
		if self.item is not None:
			self.item.alive = False

	def kill(self):
		""" definitive kill of active game entity, removing from spawn-able item list too """
		world.objects.remove(self.item)
		self.item = None
		actors.remove(self)

class Score(Actor):
	spriteset = Spriteset.fromfile("score")

	def __init__(self, value, x, y):
		Actor.__init__(self, None, int(x), int(y))
		if value is 5:
			self.sprite.set_picture(0)
		elif value is -5:
			self.sprite.set_picture(1)
		elif value is 1:
			self.sprite.set_picture(2)

		self.t0 = window.get_ticks()
		self.t1 = self.t0 + 1000

	def update(self):
		now = window.get_ticks()
		p = (now - self.t0) / (self.t1 - self.t0)
		p = -(p * (p - 2))
		self.sprite.set_position(int(self.x - world.x), int(self.y - p*16))
		return now < self.t1

class Player(Actor):
	""" main player entity """
	size = (24, 36)
	xspeed_delta = 12
	xspeed_limit = 200
	yspeed_delta = 10
	yspeed_limit = 350
	jspeed_delta = 5
	spriteset = Spriteset.fromfile("hero")
	seq_idle = Sequence.create_sprite_sequence(spriteset, "idle", 4)
	seq_jump = Sequence.create_sprite_sequence(spriteset, "jump", 24)
	seq_run = Sequence.create_sprite_sequence(spriteset, "run", 5)

	def __init__(self):
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
			self.sprite.set_animation(type(self).seq_idle, 0)
			self.state = State.Idle
			self.xspeed = 0

	def set_running(self):
		""" sets running state, idempotent """
		if self.state is not State.Run:
			self.sprite.set_animation(type(self).seq_run, 0)
			self.state = State.Run

	def set_jump(self):
		""" sets jump state, idempotent """
		if self.state is not State.Jump:
			self.yspeed = -280
			self.sprite.set_animation(type(self).seq_jump, 0)
			self.state = State.Jump
			self.medium = Medium.Air
			sounds.play("jump", 0)

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
		sounds.play("hurt", 0)
		world.add_timer(-5)
		Score(-5, self.x, self.y)

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
			self.medium = Medium.Air
		world.pick_gem(tiles_info)

	def check_jump_on_enemies(self, x, y):
		""" checks jumping above an enemy. If so, kills it, bounces and spawns a death animation """
		px, py = x+self.width/2, y+self.height
		for actor in actors:
			actor_type = type(actor)
			if actor_type in (Eagle, Opossum):
				ex, ey = actor.x + actor.size[0]/2, actor.y
				if abs(px - ex) < 25 and 5 < py - ey < 20:
					world.add_timer(5)
					actor.kill()
					self.set_bounce()
					Effect(actor.x, actor.y - 10, spriteset_death, seq_death)
					sounds.play("crush", 2)
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
		if self.yspeed > 0:
			self.check_jump_on_enemies(intx, inty)

		if self.x != oldx or self.y != oldy:
			self.rectangle.update_position(int(self.x), int(self.y))
			self.sprite.set_position(int(self.x) - world.x, int(self.y))
		return True


class Eagle(Actor):
	""" Flying enemy """
	size = (40, 40)
	spriteset = Spriteset.fromfile("enemy_eagle")
	seq_fly = Sequence.create_sprite_sequence(spriteset, "fly", 6)

	def __init__(self, item_ref, x, y):
		Actor.__init__(self, item_ref, x, y)
		self.frame = 0
		self.base_y = y
		self.xspeed = -3
		self.direction = Direction.Left
		self.sprite.set_animation(type(self).seq_fly, 0)
		self.collision_points = (4, 20, 36)

	def update(self):
		""" Update once per frame """
		self.x += self.xspeed
		self.y = self.base_y + int(sin(radians(self.frame*4))*15)
		self.frame += 1
		if self.frame is 10:
			sounds.play("eagle", 3)
		screen_x = self.x - world.x

		if self.direction is Direction.Left:
			if screen_x < 10:
				self.direction = Direction.Right
				self.xspeed = -self.xspeed
				self.sprite.set_flags(Flags.FLIPX)
				sounds.play("eagle", 3)
			else:
				for point in self.collision_points:
					player.check_hit(self.x, self.y + point, self.direction)
		else:
			if screen_x > 590:
				self.direction = Direction.Left
				self.xspeed = -self.xspeed
				self.sprite.set_flags(0)
				sounds.play("eagle", 3)
			else:
				for point in self.collision_points:
					player.check_hit(self.x + self.size[0], self.y + point, self.direction)
		self.sprite.set_position(screen_x, self.y)
		return True

class Opossum(Actor):
	""" Floor enemy. Chases player in a 80 pixel radius """
	size = (36, 24)
	spriteset = Spriteset.fromfile("enemy_opossum")
	seq_walk = Sequence.create_sprite_sequence(spriteset, "opossum-", 6)

	def __init__(self, item_ref, x, y):
		Actor.__init__(self, item_ref, x, y)
		self.xspeed = -2
		self.direction = Direction.Left
		self.sprite.set_animation(type(self).seq_walk, 0)

	def update(self):
		""" Update once per frame """
		self.x += self.xspeed
		if self.direction is Direction.Left:
			if self.x - player.x < -80:
				self.direction = Direction.Right
				self.xspeed = -self.xspeed
				self.sprite.set_flags(Flags.FLIPX)
			else:
				player.check_hit(self.x, self.y + self.size[1]//2, self.direction)
		else:
			if self.x - player.x > 80 and self.direction is Direction.Right:
				self.direction = Direction.Left
				self.xspeed = -self.xspeed
				self.sprite.set_flags(0)
			else:
				player.check_hit(self.x + self.size[0], self.y + self.size[1]//2, self.direction)

		self.sprite.set_position(self.x - world.x, self.y)
		return True

class Effect(Actor):
	""" placeholder for simple sprite effects """
	def __init__(self, x, y, spriteset, sequence):
		self.spriteset = spriteset
		Actor.__init__(self, None, x, y)
		self.sprite.set_animation(sequence, 1)

	def update(self):
		""" updates effect state once per frame """
		self.sprite.set_position(self.x - world.x, self.y)
		if self.sprite.get_animation_state() is False:
			return False
		return True

class UI(object):
	""" UI ekements """
	def __init__(self):
		self.cols = WIDTH//8
		self.layer = engine.layers[0]
		self.layer.setup(Tilemap.create(4, self.cols, None), Tileset.fromfile("ui.tsx"))
		self.layer.set_clip(0, 0, WIDTH, 32)

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

class World(object):
	""" world/play field entity """
	def __init__(self):
		self.foreground = engine.layers[1]
		self.background = engine.layers[2]
		self.clouds = 0.0
		self.foreground.setup(Tilemap.fromfile("layer_foreground.tmx"))
		self.background.setup(Tilemap.fromfile("layer_background.tmx"))
		self.x = 0
		self.x_max = self.foreground.width - WIDTH
		self.objects = load_objects("assets/layer_foreground.tmx", "Capa de Objetos 1", 973)
		engine.set_background_color(self.background.tilemap)
		actors.append(self)

	def start(self):
		self.time = 30
		self.add_timer(0)
		ui.update_time(self.time)
	
	def pick_gem(self, tiles_list):
		""" updates tilemap when player picks a gem """
		for tile_info in tiles_list:
			if tile_info.type is Tiles.Gem:
				self.foreground.tilemap.set_tile(tile_info.row, tile_info.col, None)
				Effect(tile_info.col*16, tile_info.row*16, spriteset_vanish, seq_vanish)
				sounds.play("pickup", 1)
				self.add_timer(1)
				Score(1, tile_info.col*16, tile_info.row*16)
				break

	def add_timer(self, amount):
		""" increases/decreases timer timer """
		self.due_time = window.get_ticks() + 1000
		if amount >= 0:
			self.time += amount
		else:
			amount = -amount
			if self.time >= amount:
				self.time -= amount
			else:
				self.time = 0
		ui.update_time(self.time)

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

		now = window.get_ticks()
		if now > self.due_time:
			self.add_timer(-1)

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
		color = interpolate_color(line, 0, 128, SKY_COLORS[0], SKY_COLORS[1])
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

# set raster callback
engine.set_raster_callback(raster_effect)

actors = list()		# list that contains every active game entity
ui = UI()			# UI items
world = World()		# world/level entity
player = Player()   # player entity

# Sound effects
sounds = Sound(4, "assets")
sounds.load("jump", "jump.wav")
sounds.load("crush", "crunch.wav")
sounds.load("pickup", "pickup.wav")
sounds.load("hurt", "hurt.wav")
sounds.load("eagle", "vulture.wav")

# window creation & main loop
window = Window.create()
world.start()
while window.process():

	# update active entities list
	for actor in actors:
		if not actor.update():
			actors.remove(actor)
