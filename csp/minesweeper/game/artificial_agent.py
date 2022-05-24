#!/usr/bin/env python3
from game.minesweeper import Board, Action, ActionFactory
from random import Random
from time import perf_counter
from typing import List, Tuple


class ArtificialAgent:
    """
    Agent interface for solving minesweeper game.

    Implements core agent methods for interacting with minesweeper game:
      - new_game
      - observe
      - act
      - think
        - core logic wrapper
        - provide basic thinking:
          - always use hints
          - finish game when only mines are remaining
        - logic should be implemented in Subclass in think_impl method
          which is called by think
    """

    def __init__(self) -> None:
        self._board: Board = None
        self.verbose: int = 0
        self.random: Random = Random()

        self._previous_board: Board = None
        self._think_time = 0  # seconds

        # not visible tiles
        self.unknown: List[Tuple[int, int]] = None

    def new_game(self) -> None:
        """Agent got into a new level."""
        self._board = None
        self.unknown = None

        self._previous_board = None
        self._think_time = 0

    def observe(self, board: Board) -> None:
        """Agent receives current state of the board."""
        self._board = board

        if self.unknown:
            self.unknown[:] = [
                pos for pos in self.unknown if not board.tile(*pos).visible
            ]
        else:
            self.unknown = []
            for (x, y), tile in board.generator():
                if not tile.visible:
                    self.unknown.append((x, y))

    def act(self) -> Action:
        """Agent is queried what to do next."""
        action = self.think()
        if action is None:
            raise RuntimeError("Agent didn't devise any action.")

        if self.verbose > 1:
            print("EXECUTING: {}".format(action))
        return action

    def think(self) -> Action:
        # board state
        if self.verbose > 2:
            print("\n", self._board, sep="")

        # always use advice
        safe_pos = self._board.last_safe_tile
        if safe_pos is not None and not self._board.tile(*safe_pos).visible:
            if self.verbose > 1:
                print("took hint at ({0}, {1})".format(*safe_pos))
            return ActionFactory.get_uncover_action(*safe_pos)

        # check only mines remaining
        if len(self.unknown) == self._board.mines_count:
            for pos in self.unknown:
                if not self._board.tile(*pos).flag:
                    return ActionFactory.get_flag_action(*pos)
            raise RuntimeError(
                "Should not reach here; solution or board.mines invalid?"
            )

        # do the thinking
        if self.verbose > 1:
            print("THINKING")
        start = perf_counter()
        result = self.think_impl(self._board, self._previous_board)
        self._think_time += perf_counter() - start

        # save board think_impl has seen
        # -- mind the fact, that the next think() iteration may not invoke think_impl()
        #    due to the fact we're auto-using suggestions
        self._previous_board = self._board

        return result

    def think_impl(self, board: Board, previous_board: Board) -> Action:
        """
        Think over the 'board' and produce an 'action'; preferably using an Action method.

        Things already guaranteed:
        1) board is not fully solvable yet
        2) we do not have any new advice; if you want one, issue Action.advice().

        Parameters:
        - board: current state of the board
        - previous_board: a board from previous think
            - may be None during the first think
            - since ArtificialAgent is auto-using suggestions,
              previous_board will have uncovered suggested tile
        """
        raise NotImplementedError
