""" Game backbone, shared instances used in other modules """

# global constants
WIDTH = 640         # framebuffer width
HEIGHT = 360        # framebuffer height
MAX_LAYERS = 3      # backgroudn layers
MAX_SPRITES = 32    # max sprites
ASSETS_PATH = "../assets"

# global game objects, delayed creation

engine = ()	    # tilengine main instance
window = ()	    # tilengine window instance
actors = ()	    # list that contains every active game entity
ui = ()		    # UI items
world = ()	    # world/level instance
player = ()     # player instance
sounds = ()	    # sound effects handler
