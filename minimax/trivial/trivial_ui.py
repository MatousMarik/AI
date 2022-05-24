from trivial.trivial import TrivialGame
from typing import Optional

from minimax_templates import Strategy, GameUI


class TrivialUI(GameUI, Strategy):
    """
    Console interface for trivial game.

    Works with 1-2 strategies, if one strategy is None, player plays instead.
    """

    def __init__(
        self,
        strategy1: Optional[Strategy],
        strategy2: Optional[Strategy],
        seed: int = 0,
    ):
        assert strategy1 is not None or strategy2 is not None
        self.player = strategy1 is None or strategy2 is None
        self.s1 = self if strategy1 is None else strategy1
        self.s2 = self if strategy2 is None else strategy2
        self.quit = False

    def action(self, state) -> int:
        a = input("Your move {1-3}: ")
        if a == "q":
            self.quit = True
            return -1
        try:
            a = int(a)
        except:
            a = -1
        while a < 1 or a > 3:
            a = input("Move was invalid.\nYour move {1-3}: ")
            if a == "q":
                self.quit = True
                return -1
            try:
                a = int(a)
            except:
                a = -1
        return a

    def play_loop(self) -> None:
        while True:
            game = TrivialGame()
            state = game.initial_state()

            a = self.s1.action(state)
            if self.quit:
                break
            game.apply(state, a)

            a = self.s2.action(state)
            if self.quit:
                break
            game.apply(state, a)

            outcome = game.outcome(state)
            print(f"P1: {state[0]}, P2: {state[1]}")
            print(
                "Player 1 wins"
                if outcome > 0
                else "Player 2 wins"
                if outcome < 0
                else "Draw"
            )

            if self.player:
                print("Quit? Enter q.")
            else:
                q = input("Quit? Insert q or y: ")
                if q == "q" or q == "y":
                    break
