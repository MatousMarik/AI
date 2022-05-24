from game.agent import Agent
from game.cells import *

from typing import List


class Destroyer(Agent):
    def init_random(self, seed: Union[int, None]) -> None:
        pass

    @staticmethod
    def priority(game: Game, s: Cell, t: Cell, graph: List[List[int]]) -> int:
        me = game.current_player
        o = game.get_owner(s)
        # focus enemy
        if o != me:
            if o:
                # don't focus that much when can't beat
                if (s.mass - 1) * Game.ATTACK_MUL <= t.mass:
                    weight = 1
                else:
                    weight = 4
            else:
                weight = 3

        else:
            weight = 2
        # focus small if me else big
        weight = weight * (3 - t.size_index if o == me else t.size_index + 1)
        # focus according to graph
        if graph[s.index] and t.index in graph[s.index]:
            weight *= 2
        return weight

    @staticmethod
    def get_graph(game: Game) -> List[List[int]]:
        me = game.current_player
        g = [None] * game.num_cells
        not_done = [True] * game.num_cells
        border = []
        for ci, o in enumerate(game.owners):
            if o == me:
                if game.borders_enemy_cells(ci, me):
                    border.append(ci)

        frontier = set()
        for ci in border:
            nbs = [ni for ni in game.neighbors[ci] if game.owners[ni] != me]
            frontier.update(nbs)

        frontier2 = set()
        while len(frontier) > 0:
            for ci in frontier:
                nbs = [
                    ni
                    for ni in game.neighbors[ci]
                    if not_done[ni] and game.owners[ni] == me
                ]
                g[ci] = nbs
                frontier2.update(nbs)
            for ci in frontier:
                not_done[ci] = False
            frontier, frontier2 = frontier2, frontier
            frontier2.clear()

        # REVERSE
        graph = [[] for _ in range(game.num_cells)]
        for ni, neighbors in enumerate(g):
            if neighbors:
                for ci in neighbors:
                    graph[ci].append(ni)
        return graph

    def get_move(self, game: Game) -> List[Transfer]:
        me = game.current_player
        move = TransferMove()
        graph = Destroyer.get_graph(game)
        for cell in game.get_player_cells(me):
            target = max(
                (nb for nb in cell.neighbors),
                key=lambda nb: (
                    Destroyer.priority(game, cell, nb, graph),
                    -nb.mass,
                    nb.index,
                    nb,
                ),
            )
            if target.owner == me:
                mass = CellType.get_mass_over_min_size(cell.mass)
            else:
                min_mass = ceil(target.mass / Game.ATTACK_MUL) + 1
                if cell.mass - 1 < min_mass:
                    mass = CellType.get_mass_over_min_size(cell.mass, 1)
                    if mass < 0:
                        continue
                else:
                    mass = min_mass + CellType.get_mass_over_min_size(
                        cell.mass - min_mass
                    )
            if mass > 0:
                move.add_transfer(Transfer(cell, target, mass))
        return TransferMove.get_transfers_i(move)
