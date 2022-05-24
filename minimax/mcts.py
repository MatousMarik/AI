#!/usr/bin/env python3
from minimax_templates import *


class MCTS(Strategy):
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

    def action(self, state):
        """
        Return best action for given state.
        """
        # Your implementation goes here.
        raise NotImplementedError
