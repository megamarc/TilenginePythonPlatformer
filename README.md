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
## Acknowledge
Graphic assets are copyrighted and owned by their original authors
* Backgrounds created by ansimuth: https://ansimuz.itch.io/magic-cliffs-environment
* Player character created by Jesse M: https://jesse-m.itch.io/jungle-pack
## Change list
### WIP3
* Implemented acceleration and air control
* Added more collision points per side in the sprite: from 1x2 to 3x3
### WIP2
* implemented level interaction: platforms, walls and gems
* shows Layer::get_tile() and Tilemap::set_tile()
### WIP1
* initial version with basic character movement and constant floor
