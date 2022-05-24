#!/usr/bin/env python3
from game.dino import Game, DinoMove


class Agent:
    """
    Abstract class for dino reflex agent implementation.

    Note that you should not use any initialization since this is reflex agent.
    """

    def get_move(self, game: Game) -> DinoMove:
        raise RuntimeError("Calling abstract class method.")
