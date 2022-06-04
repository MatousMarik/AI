#!/usr/bin/env python3
from game.agent import Agent
from game.cells import *

from agents.destroyer import Destroyer
from agents.support import Support


class Combined(Agent):
    def __init__(self) -> None:
        self.agents = [Destroyer(), Support()]
        self.scores = [1] * len(self.agents)
        self.add_score_fs = [
            Combined.get_destroyer_score,
            Combined.get_support_score,
        ]
        assert len(self.agents) >= len(self.add_score_fs)
        self.random: Random = None

    def init_random(self, seed: Union[int, None] = 0) -> None:
        self.random = Random(seed)
        if seed is None:
            seed = 0
        for a in self.agents:
            a.init_random(seed + self.random.randrange(123456))

    def get_destroyer_score(self, game: Game) -> int:
        score = self.random.randrange(3)
        return score

    def get_support_score(self, game: Game) -> int:
        score = self.random.randrange(3)
        return score

    def get_move(self, game: Game) -> List[Transfer]:
        for i, f in enumerate(self.add_score_fs):
            self.scores[i] += f(self, game)

        agent_i = self.random.choices(
            range(len(self.agents)), self.scores, k=1
        )[0]
        self.scores[agent_i] = 1
        return self.agents[agent_i].get_move(game)
