# Sokoban API summary

[SKIP TO ARTIFICIAL AGENT](#artificial-agent)

## Game
Game logic is implemented in two scripts — [board.py](board.py) and [action.py](action.py).

Here are the classes and methods you might need for your agent implementation.

### class `EDirection`
Enumeration of possible directions of sokoban's actions.

### class `ETile`
Content of each tile of the board is represented by `int` value, that is obtained as a combination of bit masks  — *flags* — representing individual entities — Target, Box, Sokoban, Wall.

To check for entities on a tile you can use following class methods on the *int value*:
- `is_free` — Whether there is NO blocking entity on the tile,
        such as Sokoban, Box or Wall.
- `is_wall` — Whether there is a wall on the tile.
- `is_sokoban` — Whether there is sokoban on the tile.
- `is_box` — Whether there is a box on the tile.
- `is_target` — Whether there is a target on the tile.

### class `Board`
Represents the game state of the sokoban game. Contains all `tiles` in the grid, sokoban position and other information.
`Board` implements `__hash__` and `__eq__` so it can be used with sets and dictionaries.

Here is the list of methods you might want to use in your agent implementation:
- `clone` — Deep copy of the instance.
- `tile` — Return *int value* of tile on given position.
- `stile` — Return *int value* of tile at given direction from sokoban.
- `move_sokoban` — Move sokoban to the given direction (with no checks).
- `move_box` — Move box in the given direction from sokoban to that direction (with no checks). If *rev* move it to the opposite direction.
- `is_victory` — Whether goal state is reached.
- `on_board` — Whether tile in given direction from given position is on the board.
- `get_positions` — Get positions of movable entities.
- `set_state` — Inject positions of movable entities to the board. Board should be emptied by `unset_state` first. No checks.
- `unset_state` — Remove movable entities from the board. Use `set_state` to put it back. No checks. 
- `unset_and_get_state` — Combination of `get_positions` and `unset_state`. Remove movable entities and return it as `StateMinimal`.

You can use `StateMinimal` representation of a game state to save memory, but for the price of setting and unsetting if you actually need to apply actions to it. You can also implement your own representation of the game state, but note that you will need to implement `__hash__` and `__eq__` to use it with set or dictionary. To pass the assignment it should be sufficient to work with `Board` instances only.

### class `Action`
Interface for sokoban actions. Since raw actions are just directions to which sokoban should move, instances of that movement were created to enable execution of such movements. Consists of the following methods:
- `get_direction` — Raw direction.
- `is_possible` — Whether it is possible to perform action in given game state.
- `perform` — Apply action to given state.
- `reverse` — Reverse action in given state.

### class `Move`
Implements `Action` and represents actions that move only sokoban and no boxes. Note that you should use this class as static (read-only) and you should not need to create new instances. Instead you will use following class methods:
- `get_actions` — Return tuple of all possible Move-Actions.
- `get_action` — Return Move-Action to given direction.
- **`or_push`** — As `get_action` but if Move-Action won't be possible in given state, return Push-Action to given direction instead (that still might not be possible).

### class `Push`
The same as `Move` action above, but moves sokoban and one neighboring box. You should use it as a static class as well.

## Artificial agent
Agent interface for solving sokoban game. Can be found in [artificial_agent.py](artificial_agent.py).
Your agent implementation should subclass `ArtificialAgent`, that provides basic methods for interacting with the game. You should not modify existing functionality.

Then you will need to implement agent logic in static method `think` that gets copy of initial *board* state and parameters *optimal* and *verbose*. You can modify this state as you need. After you solve the game, you should return it as a sequence of `EDirecitons` or `Actions`.