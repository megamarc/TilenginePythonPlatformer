# Tilengine python platformer
This project aims to teach actual game mechanics using the free, cross-platform [Tilengine retro graphics engine](http://www.tilengine.org) under python.

![screenshot](screenshot.png)

## Features
The features implemented so far are:
* Two layer parallax scrolling
* Sprite and tileset animations
* Raster effects for sky gradient color, cloud motion, sea water *linescroll* and hills movement on a single background layer
* Basic list of game entities (actors)
* Three character states: idle, running and jumping
* Tileset attributes in Tiled editor: *type* and *priority*
* Player/level interaction: the player can jump on platforms, get blocked by walls and pick gems
* Inertial control and acceleration
* Slopes
* Active game entities management
* Define game entities (enemies, etc) inside tmx object layer and load into a list
* Enemy behavior and spawn active enemies from loaded entities list
* Enemies can hurt player and make it bounce
* Basic sound effects with SDL_Mixer library

## Prerequisites
This project depends on three external components that must be installed separately:

### Tilengine
http://www.tilengine.org

Each supported platform has its own methods for build or install binaries, please follow method of your own platform.

### SDL2 and SDL2_Mixer
https://www.libsdl.org/

SDL2 (Simple DirectMedia Layer) is an open-source, cross-platform library for managing windows, user input, graphics and sound. Both tilengine and this project use SDL2 internally. You must install the runtime binaries into your system.

**Windows and OSX:**

Download prebuilt binaries here:

https://www.libsdl.org/download-2.0.php

https://www.libsdl.org/projects/SDL_mixer/

**Debian-based linux:**

Open a terminal window and install directly from package manager:
```
sudo apt install libsdl2-2.0-0 libsdl2-mixer-2.0-0
```

### SDL2 python binding
http://pysdl2.readthedocs.io

You must also install the binding for using SDL2 from python language. From a terminal window type the following command:
```
pip install pysdl2
```

## Acknowledge
Graphic assets are copyrighted and owned by their original authors
* Backgrounds created by ansimuz: https://ansimuz.itch.io/magic-cliffs-environment
* Player character created by Jesse M: https://jesse-m.itch.io/jungle-pack
