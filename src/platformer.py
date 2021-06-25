""" Tilengine python platformer demo """

from tilengine import Engine, Window
from raster_effect import raster_effect
from world import World
from player import Player
from UI import UI
from sound import Sound
import game

# init tilengine
game.engine = Engine.create(game.WIDTH, game.HEIGHT, game.MAX_LAYERS, game.MAX_SPRITES, 0)
game.engine.set_load_path(game.ASSETS_PATH)

# set raster callback
game.engine.set_raster_callback(raster_effect)

# init global game entities
game.actors = list()
game.world = World()
game.player = Player()
game.ui = UI()

# load sound effects
game.sounds = Sound(4, game.ASSETS_PATH)
game.sounds.load("jump", "jump.wav")
game.sounds.load("crush", "crunch.wav")
game.sounds.load("pickup", "pickup.wav")
game.sounds.load("hurt", "hurt.wav")
game.sounds.load("eagle", "vulture.wav")

# create window & start main loop
game.window = Window.create()		
game.world.start()
while game.window.process():
    for actor in game.actors:
        if not actor.update():
            game.actors.remove(actor)
