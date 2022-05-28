#!/usr/bin/env python3
from typing import Tuple, Optional, List, Sequence
from game.enums import EDirection, ETile
from collections import namedtuple

from os.path import basename

Pos = namedtuple("Pos", "x y")


class Board:
    """
    Sokoban game-state representation.

    Implements eq and hash.

    Useful methods:
    - clone
    - tile
    - ptile
    - move_player
    - move_box
    - is_victory
    - on_board
    - set_state
    - unset_state
    - from_file
    """

    def __init__(self, width: int, height: int, *, init_tiles: bool = True):
        self.width: int = width
        self.height: int = height

        self.player: Pos = None
        self.box_count: int = 0
        self.box_in_place_count: int = 0

        self.level_name: str = None
        self.level: int = -1

        self.tiles: Tuple[bytearray] = None

        if init_tiles:
            self.tiles = tuple(bytearray(height) for _ in range(width))

        self._hash: int = None

    def clone(self) -> "Board":
        """Return deepcopy of self."""
        result = Board(self.width, self.height, init_tiles=False)
        result.tiles = tuple(c.copy() for c in self.tiles)

        result.player = self.player
        result.box_count = self.box_count
        result.box_in_place_count = self.box_in_place_count
        result._hash = self._hash
        return result

    def __hash__(self) -> int:
        if self._hash is not None:
            return self._hash
        h = 0
        for col in self.tiles[1:-1]:
            for tile in col[1:-1]:
                h = 13 * h + tile
            if h > 2**32:
                h &= (1 << 32) - 1
        self._hash = h
        return h

    def __eq__(self, __o: "Board") -> bool:
        """Note: assumes same type."""
        if self.__hash__() != __o.__hash__():
            return False
        return self.tiles[1:-1] == __o.tiles[1:-1]

    def tile(self, x: int, y: int) -> int:
        """Return tile on given position."""
        return self.tiles[x][y]

    def ptile(self, dir: EDirection) -> int:
        """Return tile at given direction from the player position."""
        return self.tiles[self.player.x + dir.dx][self.player.y + dir.dy]

    def relocate_player(self, tx: int, ty: int) -> None:
        """Teleport player (no checks)."""

        sx, sy = self.player
        self._relocate_entity(sx, sy, tx, ty)
        self.player = Pos(tx, ty)

    def move_player(self, dir: EDirection) -> None:
        """Move player in given direction (no checks)."""
        sx, sy = self.player
        tx, ty = sx + dir.dx, sy + dir.dy
        self._relocate_entity(sx, sy, tx, ty)
        self.player = Pos(tx, ty)

    def move_box(self, dir: EDirection, *, rev=False) -> None:
        """
        Move box in given direction from the player
        to that direction (no checks).

        rev=True to move it backwards.
        """
        sx, sy = self.player.x + dir.dx, self.player.y + dir.dy
        tx, ty = sx + dir.dx, sy + dir.dy

        if rev:
            sx, sy, tx, ty = tx, ty, sx, sy

        if ETile.is_target(self.tiles[tx][ty]):
            self.box_in_place_count += 1

        if ETile.is_target(self.tiles[sx][sy]):
            self.box_in_place_count -= 1

        self._relocate_entity(sx, sy, tx, ty)

    def _relocate_entity(self, sx: int, sy: int, tx: int, ty: int) -> None:
        """
        Teleport entity (no checks).

        Note: this will damage consistency of player and box_in_place_count.
        """
        self._hash = None
        entity = self.tiles[sx][sy] & ETile.ENTITY
        self.tiles[tx][ty] &= ETile.NULLIFY_ENTITY
        self.tiles[tx][ty] |= entity
        self.tiles[sx][sy] &= ETile.NULLIFY_ENTITY

    def is_victory(self) -> bool:
        """All boxes on targets."""
        return self.box_count == self.box_in_place_count

    def on_board(self, x: int, y: int, dir: EDirection) -> bool:
        """
        Return whether tile in given direction
        from given position is on the board.
        """
        tx = x + dir.dx
        if tx < 0 or tx >= self.width:
            return False
        ty = y + dir.dy
        if ty < 0 or ty >= self.height:
            return False
        return True

    def str_list(self) -> List[str]:
        return [
            ETile.str_repr(self.tiles[x][y])
            for y in range(self.height)
            for x in range(self.width)
        ]

    def int_sequence(self) -> Sequence[int]:
        return (
            self.tiles[x][y]
            for y in range(self.height)
            for x in range(self.width)
        )

    def __str__(self) -> str:
        a = self.str_list()
        return "\n".join(
            [
                " ".join(a[i : i + self.width])
                for i in range(0, self.width * self.height, self.width)
            ]
        )

    # ==============================
    # STATE EXTRACTION AND INSERTION
    # ==============================
    def get_positions(self, *, remove: bool = False) -> bytearray:
        """
        Get positions of moving entities. (for StateMinimal)
        If remove == True,  remove those entities from board.

        Return:
        bytearray - positions - two 8 bit position x and position y
        [0,1]       - PLAYER-x, PLAYER-y
        [2n, 2n+1] - nth-BOX-x, nth-BOX-y
        """
        ret = bytearray(2 + self.box_count * 2)

        ret[0:2] = self.player
        i = 2
        if remove:
            self.tiles[x][y] &= ETile.NULLIFY_ENTITY
            self.player = Pos(-1, -1)
            for x, col in enumerate(self.tiles):
                for y, t in enumerate(col):
                    if ETile.is_box(t):
                        col[y] &= ETile.NULLIFY_ENTITY
                        ret[i] = x
                        ret[i + 1] = y
                        i += 2
            self.box_in_place_count = 0
            self.box_count = 0
        else:
            for x, col in enumerate(self.tiles):
                for y, t in enumerate(col):
                    if ETile.is_box(t):
                        ret[i] = x
                        ret[i + 1] = y
                        i += 2
        return ret

    def set_state(self, state: "StateMinimal") -> None:
        """
        Adds "dynamic" state to this board.

        Board should be emptied by unset_state first.
        No checks.
        """
        l = len(state.positions)
        if l % 2 == 1:
            raise RuntimeError("Invalid State.")

        self._hash = None

        x, y = state.positions[0:2]
        self.player = Pos(x, y)
        self.tiles[x][y] |= ETile.PLAYER

        self.box_count = (l // 2) - 1
        if self.box_count == 0:
            return

        self.box_in_place_count = 0
        for x, y in zip(state.positions[2::2], state.positions[3::2]):
            self.tiles[x][y] |= ETile.BOX
            if ETile.is_target(self.tiles[x][y]):
                self.box_in_place_count += 1

    def unset_state(self, state: "StateMinimal") -> None:
        """
        Removes "dynamic" state from this board, leaves statics only.

        Use set_state to put it back.
        No checks.
        """
        x, y = state.positions[0:2]
        self.tiles[x][y] &= ETile.NULLIFY_ENTITY
        self.player = Pos(-1, -1)
        self.box_in_place_count = 0
        self.box_count = 0

        for x, y in zip(state.positions[2::2], state.positions[3::2]):
            self.tiles[x][y] &= ETile.NULLIFY_ENTITY

    def unset_and_get_state(self) -> "StateMinimal":
        """
        Removes "dynamic" state from this board, leaves statics only.
        Return removed state.

        Use set_state to put it back.
        No checks.
        """
        return StateMinimal(self.get_positions(remove=True))

    # =============
    # STATIC LOADER
    # =============

    @staticmethod
    def from_file(
        file_name: str,
        level_number: Optional[int] = None,
        *,
        skip: int = 0,
    ) -> Tuple["Board", int, int]:
        """
        Load board from the file.

        :param str file_name: path to the file
        :param int|None level_number: number of level to load, if None - load first
        :param int skip: skip lines in the file

        :return: Board, minimal_moves (if specified in file), last line of level

        """
        with open(file_name, "r") as file:
            line_number = skip
            if skip:
                for _ in range(skip):
                    next(file)
                line = skip

            # find start
            found = False
            for line in file:
                line_number += 1
                line = line[:-1]
                if line.isdigit():
                    if level_number is None:
                        found = True
                        level_number = int(line)
                        break
                    elif int(line) == level_number:
                        found = True
                        break

            if not found:
                print(
                    "Failed to find level{}.".format(
                        "" if level_number is None else " " + str(level_number)
                    )
                )
                return None, -1, -1

            # select level lines
            lines = []
            for line in file:
                if line is None:
                    line_number = -1
                    break
                if len(line) and line[0].isdigit():
                    break
                line_number += 1
                lines.append(line[:-1])

        if not lines:
            return None, -1, -1

        # find maze
        height = 0
        width = 0
        comments = False
        min_moves = -1

        for line in lines:
            if not comments and any(
                c not in ETile.get_maze_symbols() for c in line
            ):
                comments = True
            if comments:
                ls = line.split(":", 1)
                if ls[0] == "Moves" and len(ls) > 1:
                    min_moves = int(ls[1])
            else:
                height += 1
                if width < len(line):
                    width = len(line)

        if 50 < width <= 4 or 50 < height < 4:
            raise RuntimeError("Level has invalid dimensions.")

        # fill board
        board: Board = Board(width, height)

        board.level_name = (
            basename(file_name).split(".", 1)[0] + f": {level_number}"
        )

        board.level = level_number
        box_places_count = 0

        for y, row in enumerate(lines[:height]):
            prefix = True
            for x, s in enumerate(row):
                if prefix:
                    # aligning spaces
                    if s == " ":
                        board.tiles[x][y] = ETile.WALL
                        continue
                    else:
                        prefix = False
                f = ETile.flag_from_str(s)
                board.tiles[x][y] = f

                if ETile.is_target(f):
                    box_places_count += 1

                if ETile.is_box(f):
                    board.box_count += 1
                    if ETile.is_target(f):
                        board.box_in_place_count += 1
                elif ETile.is_player(f):
                    if board.player is not None:
                        raise RuntimeError("More players on the board.")
                    board.player = Pos(x, y)

            for x in range(x, width):
                board.tiles[x][y] = ETile.WALL

        if box_places_count != board.box_count:
            raise RuntimeError("Boxes and targets count mismatch.")

        return board, min_moves, line_number


class StateMinimal:
    """Runtime part of the Sokoban game state - only moving entities positions."""

    def __init__(self, positions: bytearray):
        """
        Pass positions like from Board.get_positions.
        bytearray - positions - two 8 bit position x and position y
        [0,1]       - PLAYER-x, PLAYER-y
        [2n, 2n+1] - nth-BOX-x, nth-BOX-y
        """
        self.positions = positions
        self._hash = None

    def __hash__(self) -> int:
        if self._hash is not None:
            return self._hash
        h = 0
        for p in self.positions:
            h = 13 * h + p
            if h > 2**32:
                h &= (1 << 32) - 1
        self._hash = h
        return h

    def __eq__(self, __o: "StateMinimal") -> bool:
        """Note: assumes same type."""
        if self.__hash__() != __o.__hash__():
            return False
        return self.positions == __o.positions

    def __str__(self) -> str:
        return f"StateMinimal[{str(self.positions)}]"
