#!/usr/bin/env python3
from game.action import *
from game.board import *
from game.artificial_agent import ArtificialAgent
from dead_square_detector import detect
from typing import List, Union
import sys
from time import perf_counter
from os.path import dirname

# hack for importing from parent package
sys.path.append(dirname(dirname(dirname(__file__))))
from astar import AStar
from search_templates import HeuristicProblem


class MyAgent(ArtificialAgent):
    """
    Logic implementation for Sokoban ArtificialAgent.

    See ArtificialAgent for details.
    """
    def __init__(self, optimal, verbose) -> None:
        super().__init__(optimal, verbose)  # recommended

    def new_game(self) -> None:
        """Agent got into a new level."""
        super().new_game()  # recommended

    @staticmethod
    def think(
        board: Board, optimal: bool, verbose: bool
    ) -> List[Union[EDirection, Action]]:
        
        """
        Code your custom agent here.
        You should use your A* implementation.

        You can find example implementation (without use of A*)
        in simple_agent.py.
        """
        
        prob = SokobanProblem(board)
        solution = AStar(prob)
        if not solution:
            return None

        return [a.dir for a in solution.actions]


class SokobanProblem(HeuristicProblem):
    """HeuristicProblem wrapper of Sokoban game."""

    def __init__(self) -> None:
        # Your implementation goes here.
        # Hint: __init__(self, initial_board) -> None:
        raise NotImplementedError

    def initial_state(self) -> Union[Board, StateMinimal]:
        # Your implementation goes here.
        # Hint: return self.initial_board
        raise NotImplementedError

    def actions(self, state: Union[Board, StateMinimal]) -> List[Action]:
        # Your implementation goes here.
        raise NotImplementedError

    def result(
        self, state: Union[Board, StateMinimal], action: Action
    ) -> Union[Board, StateMinimal]:
        # Your implementation goes here.
        raise NotImplementedError

    def is_goal(self, state: Union[Board, StateMinimal]) -> bool:
        # Your implementation goes here.
        raise NotImplementedError

    def cost(self, state: Union[Board, StateMinimal], action: Action) -> float:
        # Your implementation goes here.
        raise NotImplementedError

    def estimate(self, state: Union[Board, StateMinimal]) -> float:
        # Your implementation goes here.
        raise NotImplementedError
