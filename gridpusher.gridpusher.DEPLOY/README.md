# Gridpusher Prototype

## Todo

- [x] text format for levels
- [x] add boxes
- [x] boxes need to be rendered
- [x] match the look of the puzzlescript version a bit closer
    - [x] fix flipping in the non-player sprites
    - [x] make the numbers hideable
    - [x] reduce gutters (for now)
    - [x] pick a bg color (maybe even a bg tileset?)
    - [x] add a palette image
    - [x] palette system from rescue roguelike
- [x] remove the bouncing ball
- [x] add levels from puzzle script
- [x] add level goal
- [x] ...and go to the next level when you reach it
- [x] boxes turn into astronauts when you push them
- [x] push limit for boxes (configurable)
- [x] add visibility system
- [x] goal and stuff that can see the goal starts visible
- [x] undo key
- [x] integration with google sheets
- [x] rearrange sprites into `img` folder
- [x] current level indicator
- [x] lock/key
- [x] add some easing to the camera
- [x] remove push limit on crates
- [x] "pull" power that is activated by picking something up
- [x] music mixing test
- [ ] fixed up deployment system
- [ ] floating point movement with gridded rocks test
- [ ] "lighting" system
- [ ] function that walks across the grid in a given direction and finds the
      first thin
- [ ] refactored list of things the player has to make it easier to add pickups
- [ ] integrate palette
    - [ ] separate art experiments out from code experiments
- [ ] refactor 'simple' items that are just things that get drawn
- [ ] when you bump a door if the key isn't visible, it becomes visible
- [ ] hazard
- [ ] "metroidvania" level sequence

## Things to turn into examples in the future

- palette system
  - test mode
  - yaml with text labels and pixel picking
  - implementation that loads locations at startup (would have to bake down for
    distribution)
- grid system

## Reference to study

- [ ] void stranger
- [x] patrick's parablox: pretty mind bendy.  tonal presentation doesn't line
      up with design notes for us but lots of fascinating mechanics (kind of a
      super boiled down version of cocoon, with the entering/exiting scopes
      aspect of the puzzles).

## Explored Dead Ends

- crates can only be pushed twice before they lock in place
