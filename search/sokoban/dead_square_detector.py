#!/usr/bin/env python3
from game.board import Board
from game.enums import ETile
from typing import List


def detect(board: Board) -> List[List[bool]]:
    """
    Returns 2D matrix containing true for dead squares.

    Dead squares are squares, from which a box cannot possibly
     be pushed to any goal (even if Sokoban could teleport
     to any location and there was only one box).

    You should prune the search at any point
     where a box is pushed to a dead square.

    Returned data structure is
        [board_width] lists
            of [board_height] lists
                of bool values.
    (This structure can be indexed "struct[x][y]"
     to get value on position (x, y).)
    """
    return [[False for _ in range(board.height)] for _ in range(board.width)]
