"""
Demonstrates raster effects for tilengine:
- linescroll for medium layer
- gradient color for sky
"""

from tilengine import Color
import game

# sky gradient color
SKY_COLORS = (Color.fromstring("#78D7F2"), Color.fromstring("#E2ECF2"))

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

	# sky color gradient
	if 0 <= line <= 128:
		color = interpolate_color(line, 0, 128, SKY_COLORS[0], SKY_COLORS[1])
		game.engine.set_background_color(color)

	# sets cloud position at frame start
	if line == 0:
		game.world.background.set_position(int(game.world.clouds), 0)

	# linescroll on main background
	elif 160 <= line <= 208:
		pos1 = game.world.x//10
		pos2 = game.world.x//3
		xpos = lerp(line, 160, 208, pos1, pos2)
		game.world.background.set_position(xpos, 0)

	# bottom background
	elif line == 256:
		game.world.background.set_position(game.world.x//2, 0)
