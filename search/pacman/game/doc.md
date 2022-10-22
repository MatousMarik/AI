# Pac-Man game state API summary
This provides list of methods that you might need for interaction with Pac-Man game state. Note that the interface is built about main idea - all maze nodes has unique index and you access them and their content by these indices.

You can access all game state fields, but don't modify any of them.

## enum `DM`
Simple enumeration of metrics. To be used with the direction methods (below).
- PATH (precalculated - fast)
- EUCLID
- MANHATTAN
- EUCLID_SQ

## enum `Direction`
Simple enumeration of possible directions.

Note: for enumeration is recommended to use range(-1,4), that is much faster.

- NONE = -1
- UP = 0
- RIGHT = 1
- DOWN = 2
- LEFT = 3

## class `Game`

Simple implementation of Ms Pac-Man.

Provides all the methods a controller may use to

 a) query the game state,

 b) compute game-related attributes

 c) test moves by using a forward model

-  i.e., copy() followed by advanceGame()

-  (which is slow and should not be necessary for our purpose)


Note: maze data structures are meant to be immutable so the contents of `Game._maze` and `Game._graph` shall not change at any time.

### Utility methods

#### `copy`(self) -> 'Game'

Return deep copy of the game.



#### `advance_game`(self, pacman_dir: int, ghosts_dirs: List[int]) -> None

Central method that advances the game state.



---

### Properties:


#### `score`(self) -> int

Empty

#### `pac_loc`(self) -> int

Index of the node with pacman.





#### `lair_loc`(self) -> int

Index of the node with ghost lair.





#### `fruit_loc`(self) -> int

Index of the node with fruit.





#### `current_level`(self) -> int


#### `game_over`(self) -> bool

Whether the game is over.





#### `lives_remaining`(self) -> int


#### `eating_time`(self) -> int

For how many tick will pacman be able to eat ghost.





#### `level_ticks`(self) -> int


#### `total_ticks`(self) -> int


#### `ghost_locs`(self) -> List[int]

Indices of the nodes with ghosts.





#### `ghost_dirs`(self) -> List[int]

Direction of each ghost.





#### `edible_times`(self) -> List[int]

For how many tick will pacman be able to eat each ghost separately.





#### `lair_times`(self) -> List[int]

For how many tick will each ghost separately stay in lair.





---

### Getters


#### `get_reverse`(dir: int) -> int

The reverse of the direction.

#### `check_pill`(self, pill_index: int) -> bool

Whether the pill is not eaten.


#### `check_power_pill`(self, pill_index: int) -> bool

Whether the power pill is not eaten.



#### `get_pacman_neighbors`(self) -> Tuple[int, int, int, int]

The neighbors of the node where pacman currently is.



Note: In directions indices order.



:return: list of node indices





#### `get_ghost_neighbors`(self, ghost: int) -> Tuple[int, int, int, int]

The neighbors of the node at which the specified ghost currently resides.



NOTE: Since ghosts are not allowed to reverse, that neighbor is filtered out.

- Alternatively use: getNeighbor(), given curGhostLoc[-] for all directions.



:return: list of node indices





#### `get_ghost_node_neighbors`(self, node: int, dir_: int) -> Tuple[int, int, int, int]

The neighbors of the node where ghost with given direction can go.



NOTE: Since ghosts are not allowed to reverse, that neighbor is filtered out.

- Alternatively use: getNeighbor(), given curGhostLoc[-] for all directions.



:return: list of node indices





#### `get_ghost_loc`(self, ghost: int) -> int

Current node at which the ghost resides.



:return: node index





#### `get_ghost_dir`(self, ghost: int) -> int

Direction of the specified ghost.





#### `is_in_lair`(self, ghost: int) -> bool


#### `get_edible_time`(self, ghost: int) -> int


#### `is_edible`(self, ghost: int) -> bool


#### `get_eating_ghost`(self) -> int

:return: ghost index





#### `get_pills_count`(self) -> int

Total number of pills in the maze.





#### `get_power_pills_count`(self) -> int

Total number of power pills in the maze.





#### `get_lair_time`(self, ghost: int) -> int

Time left for ghost to spend in the lair.






#### `get_initial_pacman_position`(self) -> int

:return: node index





#### `get_initial_ghosts_position`(self) -> int

:return: node index





#### `get_nodes_count`(self) -> int

Total number of nodes in the graph. (with or without pills)





#### `get_x`(self, node: int) -> int

The x coordinate of the specified node.





#### `get_y`(self, node: int) -> int

The y coordinate of the specified node.





#### `get_xy`(self, node: int) -> maze.Coords

The (x, y) coordinates of the specified node.





#### `get_pill_index`(self, node: int) -> int

The pill index of the node. If it is -1, the node has no pill.

One can use the index to check whether the pill 
has already been eaten (via check_pill method),
but the index itself doesn't provide this information.





#### `get_power_pill_index`(self, node: int) -> int

The power pill index of the node. If it is -1, the node has no power pill.

One can use the index to check whether the power pill 
has already been eaten (via check_pill method),
but the index itself doesn't provide this information.





#### `get_neighbor`(self, node: int, dir: int) -> int

Returns the neighbor of node index that corresponds to direction.

In the case of no move, the same node index is returned.

If there is no neighboring node at the direction return -1.



:return: node index





#### `get_node_indices_with_pills`(self) -> List[int]

The indices to all the nodes that have pills at the beginning of the level.





#### `get_node_indices_with_power_pills`(self) -> List[int]

The indices to all the nodes that have power pills at the beginning of the level.





#### `get_junction_indices`(self) -> List[int]

The indices to all the nodes that are junctions.





#### `is_junction`(self, node: int) -> bool

#### `get_next_edible_ghost_score`(self) -> int

The score awarded for the next ghost to be eaten.





#### `get_active_pills_count`(self) -> int

The number of pills still in the maze.





#### `get_active_power_pills_count`(self) -> int

The number of power pills still in the maze.





#### `get_active_pills_indices`(self) -> List[int]

The indices of all active pills in the maze.





#### `get_active_pills_nodes`(self) -> List[int]

The node indices of all active pills in the maze.





#### `get_active_power_pills_indices`(self) -> List[int]

The indices of all active power pills in the maze.





#### `get_active_power_pills_nodes`(self) -> List[int]

The node indices of all active power pills in the maze.





#### `get_pill_node`(self, pill_index: int) -> int

Node index of the pill.





#### `get_power_pill_node`(self, power_pill_index: int) -> int

Node index of the power pill.





#### `get_num_neighbors`(self, node: int) -> int

The number of neighbors of a node: 2, 3 or 4.

Exception: lair, which has no neighbors.





#### `get_possible_dirs`(self, loc: int, dir: int = 4, include_reverse: bool = True) -> List[int]

The directions to be taken given the current location.



:return: list of direction indices





#### `get_possible_pacman_dirs`(self, include_reverse: bool) -> List[int]

:return: list of direction indices





#### `get_possible_ghost_dirs`(self, ghost: int) -> List[int]

:return: list of direction indices





#### `get_path_distance`(self, from_: int, to: int) -> int

The PATH distance from any node to any other node.



Note: precalculated - really fast





#### `get_euclidean_distance`(self, from_: int, to: int) -> float

The EUCLIDEAN distance between two nodes in the current maze.





#### `get_euclidean_sq_distance`(self, from_: int, to: int) -> float

The SQUARED EUCLIDEAN distance between two nodes in the current maze.





#### `get_manhattan_distance`(self, from_: int, to: int) -> int

The MANHATTAN distance between two nodes in the current maze.





#### `get_distance_function`(self, measure: pacman.DM) -> Union[Callable[[int, int], int], Callable[[int, int], float]]

Return distance function computing distance between two nodes
with respect to given metric.



Function gets two node indices and returns distance.





#### `get_best_dir_from`(self, from_: List[int], to: int, closer: bool = True, measure: pacman.DM = DM.PATH) -> int

Return the direction to take given some options (usually corresponding
to the neighbors of the node in question), moving either towards or
away (closer in {true, false}) using one of the four distance
measures.



:param from_: list of neighbor nodes (can contain -1)

:param to: target node

:return: direction index





#### `get_next_pacman_dir`(self, to: int, closer: bool, measure: pacman.DM) -> int

The direction Pac-Man should take to approach/retreat a target (to)
given some distance measure.



:return: direction index





#### `get_next_ghost_dir`(self, ghost: int, to: int, closer: bool, measure: pacman.DM) -> int

The direction ghost should take to approach/retreat a target (to)
given some distance measure. Reversals are filtered.



:return: direction index





#### `get_path`(self, from_: int, to: int) -> List[int]

Returns the path of adjacent nodes from one node to another,
including these nodes.



- E.g., path from a to c might be [a,f,r,t,o,c]



:return: list of node indices





#### `get_ghost_path`(self, ghost: int, to: int) -> List[int]

Similar to 'get_path' but takes into consideration the fact
that ghosts may not reverse. Hence the path to be taken
may be significantly longer than the shortest available path.



:return: list of node indices





#### `get_ghost_path_distance`(self, ghost: int, to: int) -> int

The path distance for a particular ghost: takes into account
the fact that ghosts may not reverse.





#### `get_target`(self, from_: int, targets: List[int], nearest: bool, measure: pacman.DM) -> int

Returns the node from 'targets' that is nearest/farthest
from the node 'from_' given the distance measure specified.



:return: node index





#### `get_ghost_target`(self, ghost: int, targets: List[int], nearest: bool) -> int

The target nearest/farhest from the position of the ghost,
considering that reversals are not allowed.



:return: node index





#### `get_fruit_type`(self) -> int


#### `get_fruit_value`(self) -> int

Return score gain for eating current fruit.
0 if there is no fruit.





