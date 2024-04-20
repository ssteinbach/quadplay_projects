# R E A C H

## Overview

A streamlined, sci-fi fantasy 4x game in a rich and detailed universe.

## TODO

* need actual tiles to render this map now
* next step is to do the erosions
* get the palette mode working again
* map colors/tiles in the debug viewer into specific palettes per layer
* separate wetness and elevation from one another?

## DONE

* tile types are more than 10, ascii rep is broken (but was handy to get started!)
    * could reduce the number of tile types or bite the bullet and go with
      something more scalable
    * generate images maybe? CSV?
    * ASCII for now - character codes for tile types

## References

* [Thinker Map Generation Algorithm](https://github.com/induktio/thinker/blob/master/src/map.cpp) -- alpha centaurji mod with "better" map generation, their algorithm.  See [world_generation function](https://github.com/induktio/thinker/blob/f7bcf03e481ef893916c496bd3d53e40d823bea2/src/map.cpp#L789)
* [Alpha Centauri Map Generation features](https://procedural-generation.isaackarth.com/2017/01/19/sid-meiers-alpha-centauri-there-are-a-number-of.html) write up on features of the AC map generator
* [Alpha Centauri wiki](https://alphacentauri.fandom.com/wiki/Customizing_the_map) wiki notes on map generation features
* [Alpha Centaur play log](http://www.dos486.com/alpha/speed2/) might be interesting for details of gameplay itself
* [Civ 1 Map Gen Algorithm](https://forums.civfanatics.com/threads/civ1-map-generation-explained.498630/) detailed description of civ1 map generation algorithm

