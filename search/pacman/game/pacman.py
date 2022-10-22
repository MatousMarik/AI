#!/usr/bin/env python3
from enum import Enum, auto, IntEnum
from typing import List, Optional, Tuple, Callable, Union
from game.maze import Maze, Node, Coords
from random import Random
from math import sqrt
from copy import deepcopy


class DM(Enum):
    """Simple enumeration of metrics. To be used with the direction methods (below)."""

    PATH = auto()  # precalculated - fast
    EUCLID = auto()
    MANHATTAN = auto()
    EUCLID_SQ = auto()


class Direction(IntEnum):
    """Note: for enumeration is recommended to use range(-1,4), that is much faster."""

    NONE = -1
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Game:
    """
    Simple implementation of Ms Pac-Man.
    Provides all the methods a controller may use to
     a) query the game state,
     b) compute game-related attributes
     c) test moves by using a forward model
         i.e., copy() followed by advanceGame()
         (which is slow and should not be necessary for our purpose)

    You can find getters under "GETTERS" comment bellow.
    """

    PILL = 10
    POWER_PILL = 50

    GHOST_EAT_SCORE = 200
    EDIBLE_TIME = 200
    EDIBLE_ALERT = 30
    EDIBLE_TIME_REDUCTION = 0.9

    LAIR_TIMES = (40, 70, 100, 130)
    COMMON_LAIR_TIME = 40
    LAIR_REDUCTION = 0.9

    LEVEL_LIMIT = 3000
    GHOST_REVERSAL = 0.0015
    MAX_LEVLES = 16
    EXTRA_LIFE_SCORE = 10000

    EAT_DISTANCE = 2

    NUM_GHOSTS = 4

    NUM_LIVES = 3
    INITIAL_PAC_DIR = 3
    INITIAL_GHOST_DIRS = (3, 3, 3, 3)

    GHOST_SPEED_REDUCTION = 2

    DX = (0, 1, 0, -1)
    DY = (-1, 0, 1, 0)

    FRUIT_VALUE = (100, 200, 500, 700, 1000, 2000, 5000)

    def __init__(self, seed: Optional[int] = None) -> None:
        self._mazes: List[Maze] = [Maze(i) for i in range(4)]
        self._rnd: Random = Random(seed)

        self.current_maze: int = 0
        self._maze: Maze = None
        self._graph: List[Node] = None

    def new_game(
        self, *, seed=None, level: int = 1, levels_to_play: int = -1
    ) -> None:
        if seed is not None:
            self._rnd = Random(seed)
        self.remaining_levels: int = levels_to_play
        self._set_level(level)
        self._score: int = 0
        self._total_time: int = 0
        self._lives_remaining: int = self.NUM_LIVES
        self._game_over: bool = False
        self.extra_life: bool = False

        self._new_board()
        self._initialize_level(new_level=False)

    def copy(self) -> "Game":
        """Return deep copy of the game."""
        return deepcopy(self)

    def _change_maze(self, index: int) -> None:
        self.current_maze = index
        self._maze = self._mazes[index]
        self._graph = self._maze.graph

    def _set_level(self, level: int) -> None:
        self._current_level: int = level
        if level <= 2:
            self._change_maze(0)
        elif level <= 5:
            self._change_maze(1)
        else:
            self._change_maze(2 + (level - 6) // 4 % 2)

    def _new_board(self) -> None:
        self._level_time: int = 0
        self._pills: List[bool] = [True] * self._maze.pill_count
        self._power_pills: List[bool] = [True] * self._maze.power_pill_count
        self.fruits_left: int = 2

    def _initialize_level(self, new_level: bool) -> None:
        if new_level:
            if self.remaining_levels > 1:
                self.remaining_levels -= 1
            elif self.remaining_levels == 1:
                self._game_over = True
                return

            self._set_level(self._current_level + 1)
            self._new_board()

        self._pac_loc: int = self._maze.pac_pos
        self.pac_dir: int = 3
        self._ghost_locs: List[int] = [self._maze.ghost_pos] * self.NUM_GHOSTS
        self._ghost_dirs: List[int] = [*self.INITIAL_GHOST_DIRS]

        self.lair_x: List[int] = [-1] * 4
        self.lair_y: List[int] = [-1] * 4

        for i in range(1, 4):
            self._place_in_lair(i)

        self._edible_times: List[int] = [0] * self.NUM_GHOSTS
        self.ghost_eat_multiplier: int = 1
        self._lair_times: List[int] = [
            int(lt * self.LAIR_REDUCTION ** (self._current_level - 1))
            for lt in self.LAIR_TIMES
        ]
        self._eating_time: int = 0
        self.dying_time: int = 0
        self._fruit_loc: int = -1
        self.ate_fruit_time: int = 0

    # ===============================================================
    #                         GAME PLAY
    # ===============================================================

    def _place_in_lair(self, index: int) -> None:
        loc = self._maze.lair_pos
        self._ghost_locs[index] = loc
        offset = 0 if index == 2 else 2 if index == 3 else 1
        self.lair_x[index] = self.get_x(loc) + 8 * offset
        self.lair_y[index] = self.get_y(loc) + 2
        self._ghost_dirs[index] = (
            Direction.UP if offset == 1 else Direction.DOWN
        )

    def _action_paused(self) -> bool:
        if self._eating_time > 0:
            self._eating_time -= 1
            if self._eating_time == 0:
                self._edible_times[self.eating_ghost] = 0
                self._lair_times[self.eating_ghost] = int(
                    self.COMMON_LAIR_TIME
                    * self.LAIR_REDUCTION ** (self._current_level - 1)
                )
                self._place_in_lair(self.eating_ghost)
            return True

        if self.dying_time > 0:
            self.dying_time -= 1
            if self.dying_time == 0:
                self._lives_remaining -= 1
                if self._lives_remaining <= 0:
                    self._game_over = True
                else:
                    self._initialize_level(False)
            return True
        return False

    def _update_fruit(self) -> None:
        maze = self._maze
        self.ate_fruit_time -= 1
        if self._fruit_loc == -1:
            active_pills_count = sum(self._pills)
            if (
                maze.pill_count - active_pills_count == 64
                and self.fruits_left == 2
                or active_pills_count == 66
                and self.fruits_left > 0
            ):
                # spawn fruit
                start_x = [0] * 4
                count = 0

                for n in maze.graph:
                    nx = n.coords.x
                    if nx == 0 or nx == 108:  # edge
                        start_x[count] = n.node_index
                        count += 1

                if not count:
                    raise RuntimeError("Can't find tunnels.")

                self._fruit_loc = start_x[self._rnd.randrange(count)]
                self.fruit_type: int = (
                    self._current_level - 1
                    if self._current_level <= 7
                    else self._rnd.randrange(7)
                )
                self.fruit_dir: int = (
                    Direction.RIGHT
                    if self.get_x(self._fruit_loc) == 0
                    else Direction.LEFT
                )
                self.fruits_left -= 1
        else:
            # fruit exists
            if self._level_time % 2 == 0:
                dir = self._rnd.choice(
                    self.get_possible_dirs(
                        self._fruit_loc, self.fruit_dir, False
                    )
                )
                self.fruit_dir = dir
                loc = self.get_neighbor(self._fruit_loc, dir)
                self._fruit_loc = loc
                x = self.get_x(loc)
                if x == 0 or x == 108:
                    # fruit goes to the tunnel - is gone
                    self._fruit_loc = -1
                    return
            else:
                dir = self.fruit_dir
                loc = self._fruit_loc

            distance = self.get_path_distance(self._pac_loc, loc)
            if distance != -1 and distance <= self.EAT_DISTANCE:
                self._score += self.FRUIT_VALUE[self.fruit_type]
                self.ate_fruit_time = 20
                self.ate_fruit_loc: int = loc
                self.ate_fruit_type: int = self.fruit_type
                self._fruit_loc = -1

    def _update_pacman(self, dir: int) -> None:
        """Updates the location of Ms Pac-Man."""
        dir = self._check_pac_dir(dir)
        self.pac_dir = dir
        self._pac_loc = self.get_neighbor(self._pac_loc, dir)

    def _check_pac_dir(self, dir: int) -> int:
        """Checks the direction and substitutes for a legal one if necessary."""
        neighbors = self._graph[self._pac_loc].neighbors
        lpd = self.pac_dir
        if (dir > 3 or dir < 0 or neighbors[dir] == -1) and (
            lpd > 3 or lpd < 0 or neighbors[lpd] == -1
        ):
            return 4

        if dir < 0 or dir > 3:
            dir = lpd

        if neighbors[dir] == -1:
            if neighbors[lpd] != -1:
                dir = lpd
            else:
                dir = self.get_possible_pac_dirs(True)[0]
        return dir

    def _update_ghosts(
        self, ghosts_directions: List[int], reverse: bool
    ) -> None:
        lair_x0, lair_y0 = self.get_xy(self._maze.lair_pos)

        lx, ly = self.lair_x, self.lair_y
        lgd = self._ghost_dirs

        for g in range(Game.NUM_GHOSTS):
            if self.is_in_lair(g):
                if not self._level_time % 2:
                    lx[g] += self.DX[lgd[g]]
                    ly[g] += self.DY[lgd[g]]
                    if ly[g] <= lair_y0 - 11:  # exited lair
                        self._ghost_locs[g] = self._maze.ghost_pos
                        lgd[g] = self.INITIAL_GHOST_DIRS[g]
                    elif self._lair_times[g] > 0:
                        if ly[g] == lair_y0:
                            lgd[g] = Direction.DOWN
                        elif ly[g] == lair_y0 + 4:
                            lgd[g] = Direction.UP
                    else:
                        if lx[g] < lair_x0 + 8:
                            lgd[g] = Direction.RIGHT
                        elif lx[g] > lair_x0 + 8:
                            lgd[g] = Direction.LEFT
                        else:
                            lgd[g] = Direction.UP
            else:
                if reverse:
                    lgd[g] = self.get_reverse(lgd[g])
                    self._ghost_locs[g] = self.get_neighbor(
                        self._ghost_locs[g], lgd[g]
                    )
                elif (
                    not self._edible_times[g]
                    or self._edible_times[g] % self.GHOST_SPEED_REDUCTION != 0
                ):
                    ghosts_directions[g] = self._check_ghost_dir(
                        g, ghosts_directions[g]
                    )
                    lgd[g] = ghosts_directions[g]
                    self._ghost_locs[g] = self.get_neighbor(
                        self._ghost_locs[g], ghosts_directions[g]
                    )

    def _check_ghost_dir(self, g: int, dir: int) -> int:
        """Checks the directions and substitutes for a legal ones if necessary."""
        lgd = self._ghost_dirs
        if dir < 0 or dir > 3:
            dir = lgd[g]

        neighbors = self.get_ghost_neighbors(g)

        if neighbors[dir] == -1:
            if neighbors[lgd[g]] != -1:
                dir = lgd[g]
            else:
                dir = self.get_possible_ghost_dirs(g)[0]
        return dir

    def _eat_pill(self) -> None:
        pill_index = self._graph[self._pac_loc].pill_index
        if pill_index > -1 and self._pills[pill_index]:
            self._score += self.PILL
            self._pills[pill_index] = False

    def _eat_power_pill(self) -> bool:
        """Eats power pill or possibly reverse ghosts."""
        reverse = False
        pill_index = self._graph[self._pac_loc].power_pill_index
        if pill_index > -1 and self._power_pills[pill_index]:
            self._score += self.POWER_PILL
            self._power_pills[pill_index] = False
            self.ghost_eat_multiplier = 1

            new_edible_time = int(
                self.EDIBLE_TIME
                * self.EDIBLE_TIME_REDUCTION ** (self._current_level - 1)
            )

            self._edible_times = [new_edible_time] * self.NUM_GHOSTS

            reverse = True
        elif self._level_time > 1 and self._rnd.random() < self.GHOST_REVERSAL:
            # random ghost reversal
            reverse = True
        return reverse

    def _eat(self) -> None:
        """Characters eat one another if possible."""
        for g, g_loc in enumerate(self._ghost_locs):
            distance = self.get_path_distance(self._pac_loc, g_loc)
            if distance != -1 and distance <= self.EAT_DISTANCE:
                if self._edible_times[g] > 0:
                    # pacman eats ghost
                    self.eating_score: int = (
                        self.GHOST_EAT_SCORE * self.ghost_eat_multiplier
                    )
                    self.eating_ghost: int = g
                    self._eating_time = 12
                    self._score += self.eating_score
                    self.ghost_eat_multiplier *= 2
                    break  # only eat one ghost at the time
                else:
                    # ghost eats pacman
                    self.dying_time = 20
        for i in range(self.NUM_GHOSTS):
            if self._edible_times[i] > 0:
                self._edible_times[i] -= 1

    def _check_level_state(self) -> None:
        """
        Checks the state of the level/game
        and advances to the next level or terminates the game.
        """
        # if all pills have been eaten
        if not (any(self._pills) or any(self._power_pills)):
            pass
        #  or the time is up...
        elif self._level_time >= self.LEVEL_LIMIT:
            # award any remaining pills to Ms Pac-Man
            self._score += Game.PILL * sum(self._pills)
            self._score += Game.POWER_PILL * sum(self._power_pills)
        else:
            return

        # put a cap on the total number of levels played
        if self._current_level == self.MAX_LEVLES:
            self._game_over = True
        else:
            self._initialize_level(True)

    def advance_game(
        self,
        pacman_dir: int,
        ghosts_dirs: List[int],
    ) -> None:
        """Central method that advances the game state."""
        if self._action_paused():
            return None

        self._update_pacman(pacman_dir)
        self._eat_pill()
        reverse = self._eat_power_pill()
        if ghosts_dirs:
            self._update_ghosts(ghosts_dirs, reverse)

        self._eat()
        if ghosts_dirs:
            for g in range(self.NUM_GHOSTS):
                if self._lair_times[g] > 0:
                    self._lair_times[g] -= 1
        self._update_fruit()
        if not self.extra_life and self._score >= self.EXTRA_LIFE_SCORE:
            # award 1 extra life at 10000 points
            self.extra_life = True
            self._lives_remaining += 1

        self._total_time += 1
        self._level_time += 1
        self._check_level_state()

    # ===============================================================
    #                            GETTERS
    # ===============================================================

    @property
    def score(self) -> int:
        return self._score

    @property
    def pac_loc(self) -> int:
        """Index of the node with pacman."""
        return self._pac_loc

    @property
    def lair_loc(self) -> int:
        """Index of the node with ghost lair."""
        return self._maze.lair_pos

    @property
    def fruit_loc(self) -> int:
        """Index of the node with fruit."""
        return self._fruit_loc

    @property
    def current_level(self) -> int:
        return self._current_level

    @property
    def game_over(self) -> bool:
        """Whether the game is over."""
        return self._game_over

    @property
    def lives_remaining(self) -> int:
        return self._lives_remaining

    @property
    def eating_time(self) -> int:
        """For how many tick will pacman be able to eat ghost."""
        return self._eating_time

    @property
    def level_ticks(self) -> int:
        return self._level_time

    @property
    def total_ticks(self) -> int:
        return self._total_time

    @property
    def ghost_locs(self) -> List[int]:
        """Indices of the nodes with ghosts."""
        return [*self._ghost_locs]

    @property
    def ghost_dirs(self) -> List[int]:
        """Direction of each ghost."""
        return [*self._ghost_dirs]

    @property
    def edible_times(self) -> List[int]:
        """For how many tick will pacman be able to eat each ghost separately."""
        return [*self._edible_times]

    @property
    def lair_times(self) -> List[int]:
        """For how many tick will each ghost separately stay in lair."""
        return [*self._lair_times]

    @staticmethod
    def get_reverse(dir: int) -> int:
        """The reverse of the direction."""
        if dir == 0:
            return 2
        elif dir == 1:
            return 3
        elif dir == 2:
            return 0
        elif dir == 3:
            return 1
        return -1

    def check_pill(self, pill_index: int) -> bool:
        """Whether the pill is not eaten."""
        return self._pills[pill_index]

    def check_power_pill(self, pill_index: int) -> bool:
        """Whether the power pill is not eaten."""
        return self._power_pills[pill_index]

    def get_pacman_neighbors(self) -> Tuple[int, int, int, int]:
        """
        The neighbors of the node where pacman currently is.

        Note: In directions indices order.

        :return: list of node indices
        """
        return self._graph[self._pac_loc].neighbors

    def get_ghost_neighbors(self, ghost: int) -> Tuple[int, int, int, int]:
        """
        The neighbors of the node at which the specified ghost currently resides.

        NOTE: Since ghosts are not allowed to reverse, that neighbor is filtered out.
            Alternatively use: getNeighbor(), given curGhostLoc[-] for all directions.

        :return: list of node indices
        """
        return self.get_ghost_node_neighbors(
            self._ghost_locs[ghost], self._ghost_dirs[ghost]
        )

    def get_ghost_node_neighbors(
        self, node: int, dir_: int
    ) -> Tuple[int, int, int, int]:
        """
        The neighbors of the node where ghost with given direction can go.

        NOTE: Since ghosts are not allowed to reverse, that neighbor is filtered out.
            Alternatively use: getNeighbor(), given curGhostLoc[-] for all directions.

        :return: list of node indices
        """
        rev = self.get_reverse(dir_)
        nb = self._graph[node].neighbors

        if nb[rev] == -1:
            return nb

        nb = list(nb)
        nb[rev] = -1
        return tuple(nb)

    def get_ghost_loc(self, ghost: int) -> int:
        """
        Current node at which the ghost resides.

        :return: node index
        """
        return self._ghost_locs[ghost]

    def get_ghost_dir(self, ghost: int) -> int:
        """Direction of the specified ghost."""
        return self._ghost_dirs[ghost]

    def is_in_lair(self, ghost: int) -> bool:
        return self._ghost_locs[ghost] == self._maze.lair_pos

    def get_edible_time(self, ghost: int) -> int:
        return self._edible_times[ghost]

    def is_edible(self, ghost: int) -> bool:
        return self._edible_times[ghost] > 0

    def get_eating_ghost(self) -> int:
        """:return: ghost index"""
        return self.eating_ghost if self._eating_time > 0 else -1

    def get_pills_count(self) -> int:
        """Total number of pills in the maze."""
        return self._maze.pill_count

    def get_power_pills_count(self) -> int:
        """Total number of power pills in the maze."""
        return self._maze.power_pill_count

    def get_lair_time(self, ghost: int) -> int:
        """Time left for ghost to spend in the lair."""
        return self._lair_times[ghost]

    def ghost_requires_action(self, ghost: int) -> bool:
        """If in lair (getLairTime(-)>0) or if not at junction."""
        return self.is_junction(self._ghost_locs[ghost]) and (
            self._edible_times[ghost] == 0
            or self._edible_times[ghost] % self.GHOST_SPEED_REDUCTION != 0
        )

    def get_initial_pacman_position(self) -> int:
        """:return: node index"""
        return self._maze.pac_pos

    def get_initial_ghosts_position(self) -> int:
        """:return: node index"""
        return self._maze.ghost_pos

    def get_nodes_count(self) -> int:
        """Total number of nodes in the graph. (with or without pills)"""
        return self._maze.graph_size

    def get_x(self, node: int) -> int:
        """The x coordinate of the specified node."""
        return self._graph[node].coords.x

    def get_y(self, node: int) -> int:
        """The y coordinate of the specified node."""
        return self._graph[node].coords.y

    def get_xy(self, node: int) -> Coords:
        """The (x, y) coordinates of the specified node."""
        return self._graph[node].coords

    def get_pill_index(self, node: int) -> int:
        """
        The pill index of the node. If it is -1, the node has no pill.
        One can use the index to check whether the pill
        has already been eaten (via check_pill method),
        but the index itself doesn't provide this information.
        """
        return self._graph[node].pill_index

    def get_power_pill_index(self, node: int) -> int:
        """
        The power pill index of the node. If it is -1, the node has no power pill.
        One can use the index to check whether the power pill
        has already been eaten (via check_pill method),
        but the index itself doesn't provide this information.
        """
        return self._graph[node].power_pill_index

    def get_neighbor(self, node: int, dir: int) -> int:
        """
        Returns the neighbor of node index that corresponds to direction.
        In the case of no move, the same node index is returned.
        If there is no neighboring node at the direction return -1.

        :return: node index
        """
        if 0 <= dir <= 3:
            return self._graph[node].neighbors[dir]
        else:
            return node

    def get_node_indices_with_pills(self) -> List[int]:
        """The indices to all the nodes that have pills at the beginning of the level."""
        return [*self._maze.pills]

    def get_node_indices_with_power_pills(self) -> List[int]:
        """The indices to all the nodes that have power pills at the beginning of the level."""
        return [*self._maze.power_pills]

    def get_junction_indices(self) -> List[int]:
        """The indices to all the nodes that are junctions."""
        return [*self._maze.junctions]

    def is_junction(self, node: int) -> bool:
        return self._graph[node].num_neighbors > 2

    def get_next_edible_ghost_score(self) -> int:
        """The score awarded for the next ghost to be eaten."""
        return self.GHOST_EAT_SCORE * self.ghost_eat_multiplier

    def get_active_pills_count(self) -> int:
        """The number of pills still in the maze."""
        return sum(self._pills)

    def get_active_power_pills_count(self) -> int:
        """The number of power pills still in the maze."""
        return sum(self._power_pills)

    def get_active_pills_indices(self) -> List[int]:
        """The indices of all active pills in the maze."""
        return [i for i, v in enumerate(self._pills) if v]

    def get_active_pills_nodes(self) -> List[int]:
        """The node indices of all active pills in the maze."""
        nodes = self._maze.pills
        return [nodes[i] for i, v in enumerate(self._pills) if v]

    def get_active_power_pills_indices(self) -> List[int]:
        """The indices of all active power pills in the maze."""
        return [i for i, v in enumerate(self._power_pills) if v]

    def get_active_power_pills_nodes(self) -> List[int]:
        """The node indices of all active power pills in the maze."""
        nodes = self._maze.power_pills
        return [nodes[i] for i, v in enumerate(self._power_pills) if v]

    def get_pill_node(self, pill_index: int) -> int:
        """Node index of the pill."""
        return self._maze.pills[pill_index]

    def get_power_pill_node(self, power_pill_index: int) -> int:
        """Node index of the power pill."""
        return self._maze.power_pills[power_pill_index]

    def get_num_neighbors(self, node: int) -> int:
        """
        The number of neighbors of a node: 2, 3 or 4.
        Exception: lair, which has no neighbors.
        """
        self._graph[node].num_neighbors

    def get_possible_dirs(
        self, loc: int, dir: int = 4, include_reverse: bool = True
    ) -> List[int]:
        """
        The directions to be taken given the current location.

        :return: list of direction indices
        """
        if self._graph[loc].num_neighbors == 0:
            return []

        nbs = self._graph[loc].neighbors
        if include_reverse or (dir < 0 or dir > 3):
            return [i for i, n in enumerate(nbs) if n != -1]
        else:
            rev = self.get_reverse(dir)
            return [i for i, n in enumerate(nbs) if n != -1 and i != rev]

    def get_possible_pacman_dirs(self, include_reverse: bool) -> List[int]:
        """:return: list of direction indices"""
        return self.get_possible_dirs(
            self._pac_loc, self.pac_dir, include_reverse
        )

    def get_possible_ghost_dirs(self, ghost: int) -> List[int]:
        """:return: list of direction indices"""
        return self.get_possible_dirs(
            self._ghost_locs[ghost], self._ghost_dirs[ghost], False
        )

    def get_path_distance(self, from_: int, to: int) -> int:
        """
        The PATH distance from any node to any other node.

        Note: precalculated - really fast
        """
        if from_ == to:
            return 0
        if from_ < to:
            return self._maze.distances[((to * (to + 1)) // 2) + from_]
        return self._maze.distances[((from_ * (from_ + 1)) // 2) + to]

    def get_euclidean_distance(self, from_: int, to: int) -> float:
        """The EUCLIDEAN distance between two nodes in the current maze."""
        fx, fy = self._graph[from_].coords
        tx, ty = self._graph[to].coords
        return sqrt((fx - tx) ** 2 + (fy - ty) ** 2)

    def get_euclidean_sq_distance(self, from_: int, to: int) -> float:
        """The SQUARED EUCLIDEAN distance between two nodes in the current maze."""
        fx, fy = self._graph[from_].coords
        tx, ty = self._graph[to].coords
        return (fx - tx) ** 2 + (fy - ty) ** 2

    def get_manhattan_distance(self, from_: int, to: int) -> int:
        """The MANHATTAN distance between two nodes in the current maze."""
        fx, fy = self._graph[from_].coords
        tx, ty = self._graph[to].coords
        return abs(fx - tx) + abs(fy - ty)

    def get_distance_function(
        self, measure: DM
    ) -> Union[Callable[[int, int], int], Callable[[int, int], float]]:
        """
        Return distance function computing distance between two nodes
        with respect to given metric.

        Function gets two node indices and returns distance.
        """
        if measure is DM.PATH:
            return self.get_path_distance
        elif measure is DM.EUCLID:
            return self.get_euclidean_distance
        elif measure is DM.MANHATTAN:
            return self.get_manhattan_distance
        elif measure is DM.EUCLID_SQ:
            return self.get_euclidean_sq_distance
        else:
            raise RuntimeError("Unknown measure.")

    def get_best_dir_from(
        self,
        from_: List[int],
        to: int,
        closer: bool = True,
        measure: DM = DM.PATH,
    ) -> int:
        """
        Return the direction to take given some options (usually corresponding
        to the neighbors of the node in question), moving either towards or
        away (closer in {true, false}) using one of the four distance
        measures.

        :param from_: list of neighbor nodes (can contain -1)
        :param to: target node
        :return: direction index
        """
        dist_f = self.get_distance_function(measure)
        min_max = min if closer else max
        _, bi = min_max(
            (
                (dist_f(node, to), i)
                for i, node in enumerate(from_)
                if node != -1
            ),
            default=(None, -1),
        )
        return bi

    def get_next_pacman_dir(self, to: int, closer: bool, measure: DM) -> int:
        """
        The direction Pac-Man should take to approach/retreat a target (to)
        given some distance measure.

        :return: direction index
        """
        return self.get_best_dir_from(
            self._graph[self._pac_loc].neighbors, to, closer, measure
        )

    def get_next_ghost_dir(
        self, ghost: int, to: int, closer: bool, measure: DM
    ) -> int:
        """
        The direction ghost should take to approach/retreat a target (to)
        given some distance measure. Reversals are filtered.

        :return: direction index
        """
        return self.get_best_dir_from(
            self.get_ghost_neighbors(ghost), to, closer, measure
        )

    def get_path(self, from_: int, to: int) -> List[int]:
        """
        Returns the path of adjacent nodes from one node to another,
        including these nodes.

            E.g., path from a to c might be [a,f,r,t,o,c]

        :return: list of node indices
        """
        path = []
        if from_ < 0 or to < 0:
            return path

        cur_node = from_

        while cur_node != to:
            path.append(cur_node)
            nbs = self._graph[cur_node].neighbors
            cur_node = nbs[self.get_best_dir_from(nbs, to, True, DM.PATH)]

        return path

    def get_ghost_path(self, ghost: int, to: int) -> List[int]:
        """
        Similar to 'get_path' but takes into consideration the fact
        that ghosts may not reverse. Hence the path to be taken
        may be significantly longer than the shortest available path.

        :return: list of node indices
        """
        path = []
        if self._graph[self._ghost_locs[ghost]].neighbors == 0:
            return

        cur_node = self._ghost_locs[ghost]
        last_dir = self._ghost_dirs[ghost]

        if cur_node == -1 or cur_node == self.lair_loc:
            return []

        while cur_node != to:
            path.append(cur_node)
            nbs = self.get_ghost_node_neighbors(cur_node, last_dir)
            last_dir = self.get_best_dir_from(nbs, to, True, DM.PATH)
            cur_node = nbs[last_dir]

        return path

    def get_ghost_path_distance(self, ghost: int, to: int) -> int:
        """
        The path distance for a particular ghost: takes into account
        the fact that ghosts may not reverse.
        """
        return len(self.get_ghost_path(ghost, to))

    def get_target(
        self, from_: int, targets: List[int], nearest: bool, measure: DM
    ) -> int:
        """
        Returns the node from 'targets' that is nearest/farthest
        from the node 'from_' given the distance measure specified.

        :return: node index
        """
        dist_f = self.get_distance_function(measure)
        min_max = min if nearest else max
        _, bt = min_max(
            ((dist_f(from_, node), node) for node in targets if node != -1),
            default=(None, -1),
        )
        return bt

    def get_ghost_target(
        self, ghost: int, targets: List[int], nearest: bool
    ) -> int:
        """
        The target nearest/farthest from the position of the ghost,
        considering that reversals are not allowed.

        :return: node index
        """
        dist_f = lambda node: len(self.get_ghost_path(ghost, node))
        min_max = min if nearest else max
        _, bt = min_max(
            ((dist_f(node), node) for node in targets),
            default=(None, -1),
        )
        return bt

    def get_fruit_type(self) -> int:
        return -1 if self._fruit_loc == -1 else self.fruit_type

    def get_fruit_value(self) -> int:
        """
        Return score gain for eating current fruit.
        0 if there is no fruit.
        """
        return 0 if self._fruit_loc == -1 else self.FRUIT_VALUE[self.fruit_type]
