#!/usr/bin/env python3
from game.dino import *
from game.agent import Agent


class Dummy_Agent(Agent):
    """Reflex agent static class for Dino game."""

    def __init__(self) -> None:
        # AGENT WON'T BE INITIALIZED, SO THIS IS FINE
        raise RuntimeError

    @staticmethod
    def get_move(game: Game) -> DinoMove:
        # for visual debugging intellisense you can use
        if Dummy_Agent.debug:
            from game.debug_game import DebugGame

            game: DebugGame = game
            t = game.add_text(Coords(10, 10), "red", "Text")
            t.text = "Hello World"
            game.add_dino_rect(Coords(-10, -10), 150, 150, "yellow")
            l = game.add_dino_line(
                Coords(0, 0), Coords(600 // game.speed, 0), "black"
            )
            l.vector.x -= Dino.HEAD_X + game.dino.head.width
            l.dxdy.update(Dino.HEAD_X + game.dino.head.width, 0)
            l.dxdy.y += 50
            if game.score % 20 == 0:
                game.add_moving_line(
                    Coords(1000, 100), Coords(1000, 500), "purple"
                )

        # Dummy implementation:
        x = game.dino.x
        for o in game.obstacles:
            if o.rect.coords.x > x and o.rect.coords.x < x + 600 // game.speed:
                if Dummy_Agent.verbose:
                    print("jumping")
                return DinoMove.UP

        return DinoMove.NO_MOVE
