#!/usr/bin/env python3
from game.board import Board, EDirection
from game.action import Action, Move
import time
from typing import List, Union
from abc import ABC, abstractstaticmethod


class ArtificialAgent(ABC):
    """
    Agent interface for solving sokoban game.

    Implements core agent methods for interacting with sokoban game:
      - new_game
      - observe
      - act

    Logic should be implemented in subclass
    in think method which is called by act.
    """

    def __init__(self, optimal: bool = False, verbose: bool = False) -> None:
        # solution should be optimal
        self.optimal: bool = optimal
        # verbose output - can be used for logging
        self.verbose: bool = verbose

        self.actions: List[Union[EDirection, Action]] = None
        self.board: Board = None  # readonly
        self.think_time: float = None  # seconds

    def new_game(self) -> None:
        """Agent got into a new level."""
        self.board = None
        self.actions = None
        self.think_time = 0

    def observe(self, board: Board) -> None:
        """Agent receives current state of the board."""
        self.board = board
        cpy = board.clone()
        start = time.perf_counter()
        self.actions = self.think(cpy, self.optimal, self.verbose)
        self.think_time += time.perf_counter() - start

        # for popping from list
        self.actions.reverse()

    def act(self) -> Action:
        """Agent is queried what to do next."""
        if self.actions:
            action = self.actions.pop()
            if self.verbose > 1:
                print("EXECUTING: {}".format(action))
            if isinstance(action, EDirection):
                action = Move.or_push(self.board, action)
            return action
        else:
            return None

    @abstractstaticmethod
    def think(
        board: Board, optimal: bool, verbose: bool
    ) -> List[Union[EDirection, Action]]:
        pass
