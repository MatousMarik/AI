#!/usr/bin/env python3
from typing import Optional, Union
from random import Random
from abc import ABC, abstractmethod


class AbstractGame(ABC):
    @abstractmethod
    def initial_state(self, seed: Optional[int] = None) -> object:
        """
        Return the initial state of the problem.

        :rtype: State
        """
        pass

    @abstractmethod
    def clone(self, state) -> object:
        """
        Returns deepcopy of a given state.

        :rtype: State
        """
        pass

    @abstractmethod
    def player(self, state) -> int:
        """
        Return which player moves next.

        1 - maximizing
        2 - minimizing
        """
        pass

    @abstractmethod
    def actions(self, state) -> list:
        """
        Return list of all available actions in a given state.
        """
        pass

    @abstractmethod
    def apply(self, state, action) -> None:
        """
        Changes state to the result of the application of a given action to it.
        """
        pass

    @abstractmethod
    def is_done(self, state) -> bool:
        """
        Return if game has finished.
        """
        pass

    @abstractmethod
    def outcome(self, state) -> float:
        """
        Return value of the utility function.

         1 - player 1 win
        -1 - player 2 win
         0 - draw

        :param state: terminal state
        """
        pass

    PLAYER_1_WIN = 1.0
    PLAYER_2_WIN = -1.0
    DRAW = 0.0


class HeuristicGame(AbstractGame):
    @abstractmethod
    def evaluate(self, state) -> float:
        """
        Return estimated outcome of the game in a given state.
        """
        pass


class Strategy(ABC):
    """Strategy IFace"""

    @abstractmethod
    def action(self, state) -> object:
        pass

    def __init__(
        self, random_or_seed: Optional[Union[int, Random]] = None
    ) -> None:
        self.random: Random = (
            random_or_seed
            if isinstance(random_or_seed, Random)
            else Random(random_or_seed)
        )

    def set_seed(self, seed: int) -> None:
        self.random.seed(seed)


class RandomStrategy(Strategy):
    """Strategy implementation."""

    def __init__(self, seed=None):
        super().__init__(seed)

    def action(self, state):
        return state.random_action(self.random)


class GameUI(ABC):
    """UI interface."""

    @abstractmethod
    def __init__(
        self,
        strategy1: Strategy,
        strategy2: Optional[Strategy] = None,
        seed: int = 0,
    ) -> None:
        pass

    def game_loop(self) -> None:
        pass
