#!/usr/bin/env python3
from game.dino import Game, DinoMove
from abc import ABC, abstractstaticmethod


class Agent(ABC):
    """
    Abstract class for dino reflex agent implementation.

    Agent class will get verbose and debug variables
    with respect to game options.

    Note that you should not modify any class variables since this is simple-reflex agent.
    """

    @abstractstaticmethod
    def get_move(game: Game) -> DinoMove:
        pass
