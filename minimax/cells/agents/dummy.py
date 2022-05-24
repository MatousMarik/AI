from game.agent import Agent
from game.cells import *

from random import Random


class Dummy(Agent):
    def init_random(self, seed: Union[int, None]) -> None:
        self.random = Random(seed)

    def get_move(self, game: Game) -> List[Transfer]:
        # DUMMY IMPLEMENTATION
        me = game.current_player
        move = TransferMove()
        for cell in game.get_player_cells(me):
            available_mass = cell.mass - CellType.MEDIUM.min_size
            to = self.random.choice(cell.neighbors)
            if available_mass * Game.ATTACK_MUL > to.mass:
                move.add_transfer(Transfer(cell, to, available_mass))
        return TransferMove.get_transfers_i(move)
