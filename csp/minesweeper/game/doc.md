# Minesweeper API summary
## Game
The game is implemented in [minesweeper.py](minesweeper.py).
Game state is instance of class `Board` and is defined by 2-dimensional list (list of lists) of `Tiles`. In this case you won't get access to all information about the state — some tiles are covered, so you will be getting only **view** of the board, that won't contain any information about covered tiles.

### class `Tile`
Represents one tile of the board as a `dataclass` containing this fields:
- `mine` — Whether there is a mine on this tile (`None` for unknown).
- `mines_around` — How many mines are in total on neighboring (maximal 8) tiles. Has value -1 if tile is not uncovered.
- `visible` — Whether the tile is visible to the agent — whether it is uncovered.
- `flag` — Whether the tile is flagged.

### class `Board`
Here is the list of methods you might want to use in your agent implementation:
- `tile` — Return tile at a given position.
- `is_possible` — Whether action is possible in given state.

The rest are methods for updating game state, but since you will be working only with its *view* representation you won't be able to use them properly.

### class `ActionFactory`
There are only 3 actions which you can make: ask for advice, uncover a tile and toggle flag on the tile. Since they all are represented by single class `Action` you can use methods of this class to create instance you need.

## Artificial agent
`ArtificialAgent` is a basic agent interface implemented in script [artificial_agent.py](artificial_agent.py) that implements core agent methods for interacting with minesweeper game. You can use `random`, `verbose` (note that in this assignment verbose can be 0, 1, 2 and 3 specifying verbose level) and `unknown` (as read-only) that holds all unknown tiles' positions.

Agent will automatically use hints — uncover advised tile. If there is no such tile it will call `think_impl`. 




