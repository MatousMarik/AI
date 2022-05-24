from game.agent import Agent
from game.cells import *

from sys import path
from os.path import dirname

# hack for importing from parent package
path.append(dirname(dirname(dirname(__file__))))
from minimax import Minimax
from mcts import MCTS
from minimax_templates import *

from random import Random


class CellsGame(HeuristicGame):
    def __init__(self) -> None:
        raise NotImplementedError

    def initial_state(self, seed: Optional[int] = None) -> object:
        raise NotImplementedError

    def clone(self, state) -> object:
        raise NotImplementedError

    def player(self, state) -> int:
        raise NotImplementedError

    def actions(self, state) -> list:
        raise NotImplementedError

    def apply(self, state, action) -> None:
        raise NotImplementedError

    def is_done(self, state) -> bool:
        raise NotImplementedError

    def outcome(self, state) -> float:
        raise NotImplementedError

    def evaluate(self, state) -> float:
        raise NotImplementedError


class SafeMove(TransferMove):
    """Example move utility."""

    def add_transfer(self, transfer: Transfer) -> None:
        if all(
            transfer.source != t.source or transfer.target == t.target
            for t in self.transfers
        ):
            self.add_and_combine_transfer(transfer)


class MyAgent(Agent):
    def init_random(self, seed: Union[int, None]) -> None:
        self.random = Random(seed)

    def get_move(self, game: Game) -> List[Transfer]:
        # DUMMY IMPLEMENTATION
        me = game.current_player
        move = SafeMove()
        for cell in game.get_player_cells(me):
            available_mass = cell.mass - CellType.MEDIUM.min_size
            to = self.random.choice(cell.neighbors)
            if available_mass * Game.ATTACK_MUL > to.mass:
                move.add_transfer(Transfer(cell, to, available_mass))
        return TransferMove.get_transfers_i(move)
