#!/usr/bin/env python3
from minimax_templates import *


class Mcts(Strategy):
    """
    Strategy implementation selecting action
    by Monte Carlo Tree-search with base strategy method.
    """

    def __init__(
        self,
        game: AbstractGame,
        base_strat: Strategy,
        limit: int,
        seed: Optional[int] = None,
    ):
        super().__init__(seed)  # initialize self.seed for simulations
        # Your implementation goes here.

        # self.limit = limit
        # ...
        raise NotImplementedError

    def set_seed(self, seed: int) -> None:
        super().set_seed(seed)
        # set seed for base strategy too!
        # self.base_strat.set_seed(seed)

    def action(self, state):
        """
        Return best action for given state.
        """
        # Your implementation goes here.
        raise NotImplementedError
