from minimax_templates import *


class Minimax(Strategy):
    """Strategy implementation selecting action by minimax with alpha-beta pruning method."""

    def __init__(
        self, game: HeuristicGame, limit: int = 0, seed: Optional[int] = None
    ) -> None:
        super().__init__(seed)  # initialize self.seed for simulations
        # Your implementation goes here.

        # self.limit = limit
        # ...
        raise NotImplementedError

    def action(self, state) -> object:
        """
        Return best action for given state.
        """
        # Your implementation goes here.
        raise NotImplementedError
