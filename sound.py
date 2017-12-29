from sdl2 import *
from sdl2.sdlmixer import *

class Sound(object):
	""" Manages sound effects """
	def __init__(self, num_channels, path):
		SDL_Init(SDL_INIT_AUDIO)
		Mix_Init(0)
		Mix_OpenAudio(MIX_DEFAULT_FREQUENCY, MIX_DEFAULT_FORMAT, 2, 2048)
		Mix_AllocateChannels(num_channels)
		self._sounds = dict()
		if path is None:
			self.path = "./"
		else:
			self.path = path + "/"

	def __del__(self):
		for s in self._sounds:
			Mix_FreeChunk(s)

	def load(self, name, file):
		self._sounds[name] = Mix_LoadWAV((self.path + file).encode())

	def play(self, name, channel):
		Mix_PlayChannel(channel, self._sounds[name], 0)
