from typing import List
from minimax_templates import HeuristicGame, Strategy


class PerfectStrategy(Strategy):
    """Perfect strategy for TrivialGame."""

    def action(self, state) -> int:
        return 3


class RandomStrategy(Strategy):
    """Random strategy for TrivialGame."""

    def action(self, state) -> int:
        return self.random.randint(1, 3)


class TrivialGame(HeuristicGame):
    """
    A trivial game. There are two moves. First player 1 chooses a number from 1 to 3,
    then player 2 chooses a number from 1 to 3. Whoever chose the higher number wins.
    """

    def initial_state(self, seed: int = None) -> List[int]:
        return [0, 0]

    def clone(self, state: List[int]) -> List[int]:
        return [*state]

    def player(self, state: List[int]) -> int:
        return 1 if state[0] == 0 else 2

    def actions(self, state: List[int]) -> List[int]:
        return [1, 2, 3]

    def apply(self, state: List[int], action: int) -> None:
        if action < 1 or action > 3:
            raise ValueError("Illegal move")

        if state[0] == 0:
            state[0] = action
        elif state[1] == 0:
            state[1] = action
        else:
            raise ValueError("Game is over")

    def is_done(self, state: List[int]) -> bool:
        return bool(state[0] and state[1])

    def outcome(self, state: List[int]) -> float:
        if state[0] > state[1]:
            return HeuristicGame.PLAYER_1_WIN
        elif state[0] == state[1]:
            return HeuristicGame.DRAW
        else:
            return HeuristicGame.PLAYER_2_WIN

    def evaluate(self, state: List[int]) -> float:
        return self.DRAW
