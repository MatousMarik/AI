#!/usr/bin/env python3
from game.cells import Game, Transfer
from typing import Union, List
from abc import ABC, abstractmethod


class Agent(ABC):
    def init_random(self, seed: Union[int, None]) -> None:
        # optional implementation
        pass

    @abstractmethod
    def get_move(self, game: Game) -> List[Transfer]:
        raise RuntimeError("Abstract method called.")
