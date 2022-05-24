#!/usr/bin/env python3
from game.dino import *
from game.agent import Agent


class MyAgent(Agent):
    """Reflex agent class for Dino game."""

    def get_move(self, game: Game) -> DinoMove:
        # # for visual debugging intellisense you can use
        # from game.debug_game import DebugGame
        # game: DebugGame = game
        # t = game.add_text(Coords(10, 10), "red", "Text")
        # t.text = "Hello World"
        # game.add_dino_rect(Coords(-10, -10), 150, 150, "yellow")
        # l = game.add_dino_line(Coords(0, 0), Coords(100, 0), "black")
        # l.dxdy.update(50, 30)
        # l.dxdy.x += 50
        # game.add_moving_line(Coords(1000, 100), Coords(1000, 500), "purple")

        # YOUR CODE GOES HERE
        return DinoMove.NO_MOVE
