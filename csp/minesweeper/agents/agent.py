#!/usr/bin/env python3
from game.minesweeper import *
from game.artificial_agent import ArtificialAgent
import sys
from os.path import dirname
from typing import List, Tuple

# hack for importing from parent package
sys.path.append(dirname(dirname(dirname(__file__))))
from csp_templates import *
from solver import Solver


class Agent(ArtificialAgent):
    """
    Logic implementation for Minesweeper ArtificialAgent.

    See ArtificialAgent for details.
    """

    def __init__(self, verbose: int) -> None:
        super().__init__(verbose)

        # you can add your instance variables here

    def new_game(self) -> None:
        """Agent got into a new level."""
        super().new_game()

        # you can reset your instance variables here

    def think_impl(self, board: Board, previous_board: Board) -> Action:
        """
        Code your custom agent here.
        The existing dummy implementation always asks for a hint.

        The Board object passed to think_impl gives you the current board state.
        Check ArtificialAgent.think_impl docstring for more info.
        """
        return ActionFactory.get_advice_action()

    def reset_lists(self, board: Board) -> None:
        """Example."""
        # reset
        self.border_unknown = []
        self.border_numbers = []
        self.flagged = []

        # query tiles
        for (x, y), tile in board.generator():
            if not tile.visible:
                if tile.flag:
                    self.flagged.append((x, y))
                # test border tile
                if self.is_border_tile(x, y, board):
                    self.border_unknown.append((x, y))
            elif tile.mines_around > 0:
                # test border tile
                if self.is_border_tile(x, y, board):
                    self.border_numbers.append((x, y))

    def is_border_tile(self, x: int, y: int, board: Board) -> bool:
        """Example."""
        width, height = board.width, board.height
        is_border = False
        for dy in range(-1 if y > 0 else 0, 2 if y < height - 1 else 1):
            if is_border:
                break
            for dx in range(-1 if x > 0 else 0, 2 if x < width - 1 else 1):
                next_tile: Tile = board.tile(x + dx, y + dy)
                if next_tile.visible:
                    is_border = True
                    break
        return is_border
