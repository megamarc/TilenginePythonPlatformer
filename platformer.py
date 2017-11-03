""" Tilengine python platformer demo """
from tilengine import *

# constants
WIDTH = 640
HEIGHT = 360
sky_color1 = Color(120, 215, 242)
sky_color2 = Color(226, 236, 242)

# Game management definitions *************************************************

class State(object):
	""" player states """
	Undefined, Idle, Run, Jump = range(4)

class Direction(object):
	""" player orientations """
	Right, Left = range(2)
	
class Tiles(object):
	""" types of tiles for sprite-terrain collision detection """
	Empty, Floor, Gem = range(3)
	
class Player(object):
	""" main player entity """
	speeds = (2, -2)
	def __init__(self):
		self.state = State.Undefined
		self.direction = Direction.Right
		self.x = 60
		self.y = world.floor
		self.xspeed = 0
		self.yspeed = 0.0
		self.sprite_index = engine.get_available_sprite()
		self.sprite = engine.sprites[self.sprite_index]
		self.animation = engine.animations[engine.get_available_animation()]
		self.sprite.setup(Spriteset.fromfile("hero"))
		self.set_idle()

	def set_idle(self):
		if self.state is not State.Idle:
			self.animation.set_sprite_animation(self.sprite_index, sequence_idle, 0)
			self.state = State.Idle
			self.xspeed = 0
		
	def set_running(self, dir):
		self.xspeed = Player.speeds[dir]
		if self.state is not State.Run:
			self.animation.set_sprite_animation(self.sprite_index, sequence_run, 0)
			self.state = State.Run
		if self.direction is not dir:
			self.direction = dir
			if self.direction is Direction.Right:
				self.sprite.set_flags(0)
			else:
				self.sprite.set_flags(Flags.FLIPX)
					
	def set_jump(self):
		if self.state is not State.Jump:
			self.yspeed = -2.5
			self.animation.set_sprite_animation(self.sprite_index, sequence_jump, 0)
			self.state = State.Jump

	def update(self):
		self.x += self.xspeed
		if self.state is State.Jump:
			self.yspeed += 0.1
			self.y += self.yspeed
			if self.y > world.floor:
				self.y = world.floor
				self.yspeed = 0.0
				self.set_idle()
		if self.x < 0:
			self.x = 0
		elif self.x > world.foreground.width:
			self.x = world.foreground.width
			
		self.sprite.set_position(self.x - world.x, int(self.y))
		return True

class World(object):
	""" world/play field entity """
	def __init__(self):
		self.foreground = engine.layers[0]
		self.background = engine.layers[1]
		self.x = 0
		self.x_max = self.foreground.width - WIDTH
		self.floor = 188
		self.clouds = 0.0
		
	def update(self):
		if player.x < 240:
			self.x = 0
		else:
			self.x = player.x - 240
		if self.x > self.x_max:
			self.x = self.x_max
		self.clouds += 0.1
			
		self.foreground.set_position(self.x, 0)
		self.background.set_position(self.x/8, 0)
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
		
	if line is 0:
		world.background.set_position(int(world.clouds), 0)
	
	elif 160 <= line <= 208:
		pos1 = world.x//10
		pos2 = world.x//3
		xpos = lerp(line, 160, 208, pos1, pos2)
		world.background.set_position(xpos, 0)
		
	elif line is 256:
		world.background.set_position(world.x//2, 0)

# init engine
engine = Engine.create(WIDTH, HEIGHT, 2, 32, 32)
engine.set_background_color(sky_color1)
engine.layers[0].setup(Tilemap.fromfile("layer_foreground.tmx"))
engine.layers[1].setup(Tilemap.fromfile("layer_background.tmx"))

# load sequences for player character
sequences = SequencePack.fromfile("hero.sqx")
sequence_idle = sequences.find_sequence("seq_idle")
sequence_jump = sequences.find_sequence("seq_jump")
sequence_run = sequences.find_sequence("seq_run")
tile_info = TileInfo()

# set raster callback
engine.set_raster_callback(raster_effect)

actors = list()		# this list contains every active game entity
world = World()		# world/level entity
player = Player()   # player entity
actors.append(world)
actors.append(player)

# window creation & main loop
window = Window.create()
while window.process():

	# user input: move character
	if player.state is not State.Jump:	
		if window.get_input(Input.RIGHT):
			player.set_running(Direction.Right)
				
		elif window.get_input(Input.LEFT):
			player.set_running(Direction.Left)
			
		else:
			player.set_idle()

		if window.get_input(Input.A):
			player.set_jump()
		
	# update active entities list
	index = 0
	while index < len(actors):
		alive = actors[index].update()
		if not alive:
			del actors[index]
		index += 1

engine.delete()
