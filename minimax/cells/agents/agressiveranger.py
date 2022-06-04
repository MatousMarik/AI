#!/usr/bin/env python3
from game.agent import Agent
from game.cells import *

from agents.destroyer import Destroyer
from agents.ranger import Ranger


class AgressiveRanger(Agent):
    def __init__(self) -> None:
        self.agents: List[Agent] = [None, Destroyer(), Ranger()]
        self.random: Random = None

    def init_random(self, seed: Union[int, None] = 0) -> None:
        self.agents[2].init_random(seed)

    def get_move(self, game: Game) -> List[Transfer]:
        return self.agents[game.current_player].get_move(game)
