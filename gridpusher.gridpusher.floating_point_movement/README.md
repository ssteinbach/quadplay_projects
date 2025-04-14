# Gridpusher Prototype

## Todo 4/12/2025

- [ ] feedback that goal is reachable
- [ ] see one beyond a cell with some if you're standing next to it
- [ ] feedback when you press undo
- [ ] indicator for number of pushes to finish a level
- [ ] feedback for how many keys you have

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
- [x] fixed up deployment system
- [ ] floating point movement with gridded rocks test
    - [x] grab the accelerators and find a profile that works thematically for
          this project
    - [~] maybe zelda style acceleration curves?
    - [x] populate the blocks as things you can run into (maybe promote them
          to entities?  I forget how to do blockers...)
    - [x] zelda style push: press against block for a half second or so, then
          it moves over and triggers a push
    - [x] connect sprite up to running
    - [x] trigger callback functions
    - [x] puller should work from anywhere (using new player system)
    - [x] door sprite update and is passable when key is picked up
    - [x] undo button works again
        - [x] undo shouldn't undo going to the next level
    - [x] shouldn't be able to pull into the cell the player is on
    - [ ] better overlap system that keeps the player sprite from overlapping
    - [ ] block sliding animation
    - [ ] minit is another one to look at as a reference, also has some block
          pushing
    - [ ] could also try zelda style pull, but I don't think we need to for now
- [ ] "lighting" system
- [ ] function that walks across the grid in a given direction and finds the
      first thing
- [ ] refactored list of things the player has to make it easier to add pickups
- [ ] integrate palette
    - [ ] separate art experiments out from code experiments
- [ ] refactor 'simple' items that are just things that get drawn
- [ ] when you bump a door if the key isn't visible, it becomes visible
- [ ] hazard
- [ ] "metroidvania" level sequence
    - [ ] rather than linear list of levels, doors that lead to a specific
          place
        - [x] add a _meta sheet that can be populated
        - [x] allow goals to go to specific levels
        - [ ] don't reset world state completely on level change
    - [ ] build a little set of levels with a metroidvania vibe

## Things to turn into examples in the future

- palette system
  - test mode
  - yaml with text labels and pixel picking
  - implementation that loads locations at startup (would have to bake down for
    distribution)
- grid system

## Reference to study

- [x] void stranger
- [ ] patrick's parablox: pretty mind bendy.  tonal presentation doesn't line
      up with design notes for us but lots of fascinating mechanics (kind of a
      super boiled down version of cocoon, with the entering/exiting scopes
      aspect of the puzzles).

## Explored Dead Ends

- crates can only be pushed twice before they lock in place
- discrete motion?
