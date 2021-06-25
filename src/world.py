""" world/play field game entity """

import xml.etree.ElementTree as ET
from tilengine import Tilemap, Spriteset, Sequence
from effect import Effect
from score import Score
from eagle import Eagle
from opossum import Opossum
import game

class Tiles:
	""" types of tiles for sprite-terrain collision detection """
	Empty, Floor, Gem, Wall, SlopeUp, SlopeDown, InnerSlopeUp, InnerSlopeDown = range(8)


class Medium:
    """ types of environments """
    Floor, Air, Ladder, Water = range(4)


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
        if self.alive is False and x < self.x < x + game.WIDTH:
            self.alive = True
            if self.type is Item.Eagle:
                Eagle(self, self.x, self.y - Eagle.size[1])
            elif self.type is Item.Opossum:
                Opossum(self, self.x, self.y - Opossum.size[1])


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
                    item_list.append(
                        Item(int(gid) - first_gid, int(x), int(y)))
            return item_list
    return None

class World(object):
	""" world/play field entity """

	def __init__(self):
		self.foreground = game.engine.layers[1]
		self.background = game.engine.layers[2]
		self.clouds = 0.0
		self.foreground.setup(Tilemap.fromfile("layer_foreground.tmx"))
		self.background.setup(Tilemap.fromfile("layer_background.tmx"))
		self.spriteset_vanish = Spriteset.fromfile("effect_vanish")
		self.seq_vanish = Sequence.create_sprite_sequence(self.spriteset_vanish, "vanish", 4)
		self.x = 0
		self.x_max = self.foreground.width - game.WIDTH
		self.objects = load_objects(game.ASSETS_PATH +
			"/layer_foreground.tmx", "Capa de Objetos 1", 973)
		game.engine.set_background_color(self.background.tilemap)
		game.actors.append(self)

	def start(self):
		self.time = 30
		self.add_timer(0)
		game.ui.update_time(self.time)

	def pick_gem(self, tiles_list):
		""" updates tilemap when player picks a gem """
		for tile_info in tiles_list:
			if tile_info.type is Tiles.Gem:
				self.foreground.tilemap.set_tile(
					tile_info.row, tile_info.col, None)
				Effect(tile_info.col*16, tile_info.row*16,
						self.spriteset_vanish, self.seq_vanish)
				game.sounds.play("pickup", 1)
				self.add_timer(1)
				Score(1, tile_info.col*16, tile_info.row*16)
				break

	def add_timer(self, amount):
		""" increases/decreases timer timer """
		self.due_time = game.window.get_ticks() + 1000
		if amount >= 0:
			self.time += amount
		else:
			amount = -amount
			if self.time >= amount:
				self.time -= amount
			else:
				self.time = 0
		game.ui.update_time(self.time)

	def update(self):
		""" updates world state once per frame """
		oldx = self.x

		if game.player.x < 240:
			self.x = 0
		else:
			self.x = int(game.player.x - 240)
		if self.x > self.x_max:
			self.x = self.x_max
		self.clouds += 0.1

		if self.x is not oldx:
			self.foreground.set_position(self.x, 0)
			self.background.set_position(self.x/8, 0)

		# spawn new entities from object list
		for item in self.objects:
			item.try_spawn(self.x)

		now = game.window.get_ticks()
		if now > self.due_time:
			self.add_timer(-1)

		return True
