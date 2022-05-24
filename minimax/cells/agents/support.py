from game.agent import Agent
from game.cells import *

from typing import List


class Support(Agent):
    def init_random(self, seed: Union[int, None]) -> None:
        self.random = Random(seed)

    @staticmethod
    def fill_needs(game: Game, cells: List[Cell], needs: List[int]) -> None:
        me = game.current_player
        for c in cells:
            if game.borders_enemy_cells(c, me):
                needs[c.index] = 1000 - c.mass
            else:
                needs[c.index] = max(0, CellType.MAXIMAL.min_size - c.mass)

    def get_move(self, game: Game) -> List[Transfer]:
        me = game.current_player
        move = TransferMove()
        needs = [0] * game.num_cells
        incomings = [0] * game.num_cells
        Support.fill_needs(game, game.get_player_cells(me), needs)
        for cell in game.get_player_cells(me):
            needs[cell.index] = 0
            available_mass = min(
                CellType.get_mass_over_min_size(
                    cell.mass + incomings[cell.index]
                ),
                cell.mass - 1,
            )
            if available_mass <= 0:
                continue
            nb = max(
                (
                    nb
                    for nb in cell.neighbors
                    if nb.owner == me
                    and needs[nb.index] - incomings[nb.index] > 0
                    and needs[nb.index] - incomings[nb.index] <= available_mass
                ),
                key=lambda n: needs[n.index] - incomings[n.index],
                default=None,
            )
            if nb:
                move.add_transfer(Transfer(cell, nb, available_mass))
                incomings[nb.index] += available_mass
                continue

            # attack
            enemy_nbs = [n for n in cell.neighbors if me != n.owner]
            self.random.shuffle(enemy_nbs)
            co = False
            for nb in enemy_nbs:
                min_mass = ceil(nb.mass / Game.ATTACK_MUL) + 1
                if available_mass > min_mass:
                    move.add_transfer(Transfer(cell, nb, available_mass))
                    co = True
                    break
            if co:
                continue

            # donate rest
            donee = max(
                (n for n in cell.neighbors),
                key=lambda n: (
                    needs[n.index] - incomings[n.index],
                    n.index,
                ),
            )
            incomings[donee.index] += available_mass
            move.add_and_combine_transfer(Transfer(cell, donee, available_mass))

        return TransferMove.get_transfers_i(move)
