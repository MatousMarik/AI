#!/usr/bin/env python3
from copy import deepcopy
from typing import List, Tuple, Generator, Optional
from dataclasses import dataclass
from random import Random


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Tile:
    """
    Tile of minesweeper board.

    mine represents whether there is a mine on the tile, None is for UNKNOWN
    """

    mine: bool = False  # None for UNKNOWN
    mines_around: int = 0
    visible: bool = False  # visible to agent
    flag: bool = False  # flagged by agent

    def is_flagged(self) -> bool:
        return self.flag

    def is_uncovered(self) -> bool:
        return self.visible

    def is_unknown(self) -> bool:
        return self.mine is None

    def clone(self, *, for_view: bool = False) -> "Tile":
        """
        Return copy of the tile.

        If for_view is True, returns modified tile, so the player won't see any additional information.
        """
        if for_view and not self.visible:
            return Tile(None, -1, False, self.flag)
        else:
            return Tile(self.mine, self.mines_around, True, self.flag)

    def __str__(self) -> str:
        if self.visible:
            if self.mine:
                return "M"
            else:
                return str(self.mines_around)
        if self.flag:
            return "F"
        return "."

    def _di_(self):
        if self.visible:
            if self.mine:
                return "M"
            else:
                return self.mines_around
        if self.flag:
            return "F"
        return "."


@dataclass
class Action:
    type: int
    x: int = None
    y: int = None


class ActionFactory:
    """Static class for creating Action instances."""

    # ACTION TYPES
    SUGGEST_SAFE_TILE = 0
    UNCOVER = 1
    FLAG = 2

    names = ["SUGGEST_SAFE_TILE", "UNCOVER", "FLAG/UNFLAG"]

    @staticmethod
    def get_uncover_action(x, y) -> Action:
        return Action(1, x, y)

    @staticmethod
    def get_flag_action(x, y) -> Action:
        """Flag or unflag."""
        return Action(2, x, y)

    @staticmethod
    def get_advice_action() -> Action:
        return Action(0)

    @staticmethod
    def action_to_string(action: Action) -> str:
        return "Action[{}{}]".format(
            ActionFactory.names[action.type],
            "" if action.type == 0 else "|{},{}".format(action.x, action.y),
        )


class Board:
    """
    Represent state of the minesweeper game.

    Main methods:
    - initialization - fills board with mines randomly and set hits
    - clone
    - get_view - observable representation of state
    - tile
    - generator
    - is_victory
    - is_possible(action)
    - apply_action(action)
        - uncover_tile(x, y)
        - flag_tile(x, y) - toggles flag
        - suggest_safe_tile - return hint
    - string representation
    """

    def __init__(
        self,
        width: int,
        height: int,
        mines: int,
        seed: int = None,
        *,
        skip_initialization: bool = False
    ) -> None:
        self.mines_count: int = mines
        self.width: int = width
        self.height: int = height
        self.tiles: List[List[Tile]] = (
            None
            if skip_initialization
            else [[Tile() for _ in range(height)] for _ in range(width)]
        )
        self.boom: bool = False
        self.last_safe_tile: Position = None

        self._safe_tiles: Tuple[List[Position], List[Position]] = None
        self._covered: int = width * height

        if not skip_initialization:
            self.init_tiles(seed)

    def init_tiles(self, seed) -> None:
        # fill mines
        rnd = Random(seed)
        positions = [
            (x, y) for x in range(self.width) for y in range(self.height)
        ]

        for x, y in rnd.sample(positions, k=self.mines_count):
            self.tiles[x][y].mine = True
            for nx in range(
                x - 1 if x > 0 else x, x + 2 if x < self.width - 1 else x + 1
            ):
                for ny in range(
                    y - 1 if y > 0 else y,
                    y + 2 if y < self.height - 1 else y + 1,
                ):
                    self.tiles[nx][ny].mines_around += 1

        # init safe tiles
        self._safe_tiles = ([], [])
        for x, col in enumerate(self.tiles):
            for y, t in enumerate(col):
                if t.mine is False:
                    if t.mines_around == 0:
                        self._safe_tiles[0].append(Position(x, y))
                    else:
                        self._safe_tiles[1].append(Position(x, y))

        rnd.shuffle(self._safe_tiles[0])
        rnd.shuffle(self._safe_tiles[1])

    def generator(self) -> Generator[Tuple[Tuple[int, int], Tile], None, None]:
        """Return generator yielding (x, y), Tile."""
        for x, col in enumerate(self.tiles):
            for y, tile in enumerate(col):
                yield (x, y), tile

    def tile(self, x, y) -> Tile:
        """Return tile at a given position."""
        return self.tiles[x][y]

    def clone(self) -> "Board":
        """Return deepcopy of self instance."""
        nb = Board(
            self.width,
            self.height,
            self.mines_count,
            0,
            skip_initialization=True,
        )
        nb.last_safe_tile = self.last_safe_tile
        nb._safe_tiles = deepcopy(self._safe_tiles)
        nb.tiles = [[t.clone() for t in col] for col in self.tiles]
        return nb

    def get_view(self) -> "Board":
        """
        Returns an agent view of the board - partially observable state, non-visible tiles are made unknown and its mines are nullified
        (value -1).
        """
        nb = Board(
            self.width,
            self.height,
            self.mines_count,
            0,
            skip_initialization=True,
        )
        nb.last_safe_tile = self.last_safe_tile
        nb.tiles = [[t.clone(for_view=True) for t in col] for col in self.tiles]
        return nb

    def is_victory(self) -> bool:
        """
        Return whether state is victorious.
        """
        if self.boom:
            return False
        return self.mines_count == self._covered

    def is_possible(self, action: Action) -> bool:
        """
        Return whether action is possible in self state.
        """
        if action.type == ActionFactory.SUGGEST_SAFE_TILE:
            return True

        if (
            action.x < 0
            or action.x >= self.width
            or action.y < 0
            or action.y >= self.height
        ):
            return False

        if action.type == ActionFactory.UNCOVER:
            return (
                not self.tiles[action.x][action.y].visible
                and not self.tiles[action.x][action.y].flag
            )
        if action.type == ActionFactory.FLAG:
            return not self.tiles[action.x][action.y].visible

        raise ValueError("Invalid action type.")

    def apply_action(self, action: Action) -> None:
        """Apply action on the given board. No checks."""
        if action.type == ActionFactory.SUGGEST_SAFE_TILE:
            self.suggest_safe_tile()
        elif action.type == ActionFactory.FLAG:
            self.flag_tile(action.x, action.y)
        elif action.type == ActionFactory.UNCOVER:
            self.uncover_tile(action.x, action.y)
        else:
            raise ValueError("Invalid action type.")

    def uncover_tile(self, x, y) -> None:
        """
        Uncover tile and if if it is empty uncover all empty tiles around.
        Note: Flagged tiles can't be uncovered
        """
        t = self.tiles[x][y]
        if t.visible or t.flag:
            return
        t.visible = True
        self._covered -= 1

        if t.mine:
            self.boom = True
            return

        if t.mines_around > 0:
            return

        # FLOOD-FILL
        # note - using lists instead of sets - expecting a little of items
        expand_positions = [(x, y)]
        found = [(x, y)]
        while expand_positions:
            x, y = expand_positions.pop()

            for dy in range(
                -1 if y > 0 else 0, 2 if y < self.height - 1 else 1
            ):
                for dx in range(
                    -1 if x > 0 else 0, 2 if x < self.width - 1 else 1
                ):
                    if dx == 0 and dy == 0:
                        continue
                    nt = self.tiles[x + dx][y + dy]
                    np = (x + dx, y + dy)
                    if nt.visible or nt.flag or np in found:
                        continue
                    found.append(np)
                    nt.visible = True
                    self._covered -= 1
                    if nt.mines_around == 0:
                        expand_positions.append(np)
        return

    def flag_tile(self, x, y) -> None:
        """For not-visible tile set flag to opposite value."""
        t = self.tile(x, y)
        if t.visible:
            return
        t.flag = not t.flag
        return

    def suggest_safe_tile(self) -> None:
        """
        Set (x, y) of safe tile or None if there is none in self.last_safe_tile.

        Only valid for Simulation-side board! I.e., calling this from agent is not fruitful!
        """
        for s in self._safe_tiles:
            while s:
                pos = s.pop()
                if self.tiles[pos.x][pos.y].visible:
                    continue
                self.last_safe_tile = pos
                return

        self.last_safe_tile = None
        return

    def __str__(self) -> str:
        a = [str(t) for col in self.tiles for t in col]
        return "\n".join(
            [
                " ".join(a[i : i + self.width])
                for i in range(0, self.width * self.height, self.width)
            ]
        )
