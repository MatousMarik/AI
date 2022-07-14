# Cell Wars API summary

## Game
The whole game logic is implemented in [cells.py](cells.py).

Here are the classes and methods you might need for your agent implementation.

### class `Game`
Represents the game state. Contains all `cells`, and their stats: `masses`, `owners`, `neighbors` (each cell has its index, that specify corresponding elements in the lists). You have option to use class representation but you can disable that option by setting `game.use_cells` to False.

Here is the list of methods you might want to use:
- `clone` — Deep copy of the instance.
- `sizes` — Size indices of all cells.
- `get_player_cells` — Cells owned by given player.
- `get_cell` — Instance of cell with given index. (use_cells has to be True all the time before the call)
- `attack` — Calculate result of transfer to enemy cell.
- `is_neighbor` — Whether cells are neighbors.
- `get_owner` — Owner of the cell/cell with index.
- `is_owned_by` — Whether cell/cell with index is owned by given player.
- `total_mass` — Sum of masses of cells controlled by given player.
- `cells_owned` — Number of cells owned by given player.
- `current_player`
- `is_done`
- `borders_enemy_cells` — Whether given cell/index has neighbor with different owner.
- `round`

### dataclass `Transfer`
Represents single transfer, list of these form one game move.

### class `TransferMove`
Utility class for creating moves. You can use this class or subclasses as in [myagent.py](../agents/myagent.py) to build single move from transfers. If you use class representation of cells you can convert your transfers with `get_transfers_i` (agent move has to be in index form).

### dataclass `CellProperties`
Represents cell types, but for technical reasons cells are not assigned their type directly, so for obtaining the type you can e.g. call methods of `CellType`.

Each type has *minimal size* and *growth*. Cell is assigned type with maximal *minimal size* that is lower or equal its mass.

### static class `CellType`
Utility class that contain methods for obtaining cell types by cells masses.

Methods:
- `get_type`
- `get_type_index`
- `get_growth`
- `get_mass_over_min_size` — Return mass available for transfer to stay in current or specified size class. Useful method for planning.

### class `Cell`
Class representing cell. Contains constants for cell growths. Instances contain these fields: `mass`, `neighbors`, `index` and `owner`.

Methods:
- `size_index`
- `type`
- `get_growth`
