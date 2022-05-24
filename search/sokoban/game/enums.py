#!/usr/bin/env python3
from enum import Enum


class ETile:
    """
    Enum flag for sokoban tiles.

    Bits (LE):
    TARGET, BOX, PLAYER, WALL
    """

    SYMBOLS = " .$*@+#"

    # FLAGS:
    NONE = 0
    PLACE = 1
    BOX = 2
    PLAYER = 4
    WALL = 8

    # COMBINED FLAGS:
    BOX_IN_PLACE = BOX | PLACE
    PLAYER_ON_PLACE = PLAYER | PLACE
    ENTITY = BOX | PLAYER
    NULLIFY_ENTITY = PLACE | WALL

    @classmethod
    def get_maze_symbols(cls) -> str:
        return cls.SYMBOLS

    @classmethod
    def is_free(cls, flag: int) -> bool:
        return flag < 2

    @classmethod
    def is_wall(cls, flag: int) -> bool:
        return flag == 8

    @classmethod
    def is_player(cls, flag: int) -> bool:
        return bool(flag & 4)

    @classmethod
    def is_box(cls, flag: int) -> bool:
        return bool(flag & 2)

    @classmethod
    def is_target(cls, flag: int) -> bool:
        return bool(flag & 1)

    # str methods are fixed hence .sok files are

    @classmethod
    def is_wall_str(cls, s: str) -> bool:
        return s == "#"

    @classmethod
    def is_free_str(cls, s: str) -> bool:
        return s != "#"

    @classmethod
    def is_player_str(cls, s: str) -> bool:
        return s in "@+"

    @classmethod
    def is_box_str(cls, s: str) -> bool:
        return s in "$*"

    @classmethod
    def for_box_str(cls, s: str) -> bool:
        return s in ".*+"

    @classmethod
    def flag_from_str(cls, s: str) -> int:
        if s == " ":
            return cls.NONE
        if s == "#":
            return cls.WALL
        if s == ".":
            return cls.PLACE
        if s == "$":
            return cls.BOX
        if s == "*":
            return cls.BOX_IN_PLACE
        if s == "@":
            return cls.PLAYER
        if s == "+":
            return cls.PLAYER_ON_PLACE
        raise RuntimeError("Invalid character.")

    @classmethod
    def str_repr(cls, flag: int) -> str:
        if 0 <= flag < len(cls.SYMBOLS):
            return cls.SYMBOLS[flag]
        return "?"


class EDirection(Enum):
    """
    Enum for sokoban movement direction.

    For enumeration you better use get_arrows.
    """

    UP = (0, 0, -1)
    RIGHT = (1, 1, 0)
    DOWN = (2, 0, 1)
    LEFT = (3, -1, 0)

    _ignore_ = ["_arrows"]
    _arrows = [UP, RIGHT, DOWN, LEFT]

    def __init__(self, index: int, dx: int, dy: int):
        self.index: int = index
        self.dx: int = dx
        self.dy: int = dy

    def opposite(self) -> "EDirection":
        if self is EDirection.UP:
            return EDirection.DOWN
        if self is EDirection.RIGHT:
            return EDirection.LEFT
        if self is EDirection.DOWN:
            return EDirection.UP
        if self is EDirection.LEFT:
            return EDirection.RIGHT
        return None

    def cw(self) -> "EDirection":
        if self is EDirection.UP:
            return EDirection.RIGHT
        if self is EDirection.RIGHT:
            return EDirection.DOWN
        if self is EDirection.DOWN:
            return EDirection.LEFT
        if self is EDirection.LEFT:
            return EDirection.UP
        return None

    def ccw(self) -> "EDirection":
        if self is EDirection.UP:
            return EDirection.LEFT
        if self is EDirection.RIGHT:
            return EDirection.UP
        if self is EDirection.DOWN:
            return EDirection.RIGHT
        if self is EDirection.LEFT:
            return EDirection.DOWN
        return None

    def __str__(self) -> str:
        return self.name
