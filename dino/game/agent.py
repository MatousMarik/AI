#!/usr/bin/env python3
from game.dino import Game, DinoMove
from abc import ABC, abstractmethod


class Agent(ABC):
    """
    Abstract class for dino reflex agent implementation.

    Note that you should not use any initialization since this is reflex agent.
    """

    @abstractmethod
    def get_move(self, game: Game) -> DinoMove:
        pass
