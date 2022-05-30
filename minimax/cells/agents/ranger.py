#!/usr/bin/env python3
from game.agent import Agent
from game.cells import *

from typing import List, Tuple, Union
from dataclasses import dataclass, astuple


MAX_INT = 2**16


@dataclass
class EnemyCell:
    min_attack: int = None
    index: int = None
    min_defense: int = None


class Ranger(Agent):
    def init_random(self, seed: Union[int, None]) -> None:
        self.random = Random(seed)
        self.key = lambda e: (
            e[0],
            self.random.randrange(MAX_INT),
            e[1],
        )
        self.enemy_key = lambda e: (
            e.min_attack - self.e_incoming[e.index][0],
            self.random.randrange(MAX_INT),
            e.index,
        )
        self.need_key = lambda e: (
            e[0],
            self.needs[e[1]] - self.incoming[e[1]],
            self.random.randrange(MAX_INT),
            e[1],
        )

    def process_game(
        self,
        game: Game,
    ) -> None:
        self.masses: List[int] = game.masses
        self.me = game.current_player

        g = [None] * game.num_cells
        not_done = [True] * game.num_cells
        self.insides: List[int] = []
        self.border: List[int] = []
        for ci, o in enumerate(game.owners):
            if o == self.me:
                if game.borders_enemy_cells(ci, self.me):
                    self.border.append(ci)

        frontier = set()
        for ci in self.border:
            nbs = [
                ni for ni in game.neighbors[ci] if game.owners[ni] == self.me
            ]
            g[ci] = nbs
            not_done[ci] = False
            frontier.update(nbs)

        frontier.difference_update(self.border)

        border_nbs_count = len(frontier)

        frontier2 = set()
        while len(frontier) > 0:
            f = list(frontier)
            self.insides.extend(f)
            for ci in frontier:
                nbs = [
                    ni
                    for ni in game.neighbors[ci]
                    if not_done[ni]
                    and ni not in frontier
                    and game.owners[ni] == self.me
                ]
                g[ci] = nbs
                frontier2.update(nbs)
            for ci in frontier:
                not_done[ci] = False
            frontier, frontier2 = frontier2, frontier
            frontier2.clear()

        # REVERSE
        self.graph: List[List[int]] = [[] for _ in range(game.num_cells)]
        for ni, neighbors in enumerate(g):
            if neighbors:
                for ci in neighbors:
                    self.graph[ci].append(ni)
        for nbs in self.graph:
            self.random.shuffle(nbs)
        self.insides.reverse()

        self.enemies: List[
            Union[None, Tuple[List[EnemyCell], List[EnemyCell]]]
        ] = [None] * game.num_cells
        self.random.shuffle(self.border)
        bn, bp = [], []

        for ci in self.border:
            en_players = [
                EnemyCell(
                    Ranger.atk_mass(game.masses[ni]),
                    ni,
                    Ranger.def_mass(game.masses[ni]),
                )
                for ni in game.neighbors[ci]
                if game.owners[ni] == 3 - self.me
            ]
            en_neutrals = [
                EnemyCell(Ranger.atk_mass(game.masses[ni]), ni)
                for ni in game.neighbors[ci]
                if game.owners[ni] == 0
            ]
            self.enemies[ci] = (en_players, en_neutrals)
            if en_players:
                bp.append(ci)
            else:
                bn.append(ci)

        self.border = bn + bp
        self.needs: List[Union[int, None]] = [None] * game.num_cells
        for ci in self.insides:
            m = self.masses[ci]
            self.needs[ci] = max(0, CellType.MAXIMAL.min_size - m)

        if self.me == 1:
            for ci in self.border:
                en_players = self.enemies[ci][0]
                if en_players:
                    self.needs[ci] = CellType.MAXIMAL.min_size + sum(
                        ep.min_defense for ep in en_players
                    )
                else:
                    self.needs[ci] = CellType.MAXIMAL.min_size
        else:
            for ci in self.border:
                en_players, en_neutrals = self.enemies[ci]
                if en_players:
                    self.needs[ci] = CellType.MAXIMAL.min_size + max(
                        e.min_attack for e in en_players
                    )
                else:
                    self.needs[ci] = CellType.MAXIMAL.min_size + max(
                        e.min_attack for e in en_neutrals
                    )
        self.first_border_nb: int = len(self.insides) - border_nbs_count
        self.incoming: List[int] = [0] * game.num_cells
        self.e_incoming: List[List[int, List[int]]] = [
            [0, []] for _ in range(game.num_cells)
        ]
        self.plans: List[Union[None, Tuple[int, List[int]]]] = [
            None
        ] * game.num_cells

    @staticmethod
    def def_mass(mass: int) -> int:
        return ceil(mass * Game.ATTACK_MUL)

    @staticmethod
    def atk_mass(mass: int) -> int:
        return ceil(mass / Game.ATTACK_MUL) + 1

    def execute_plans(self, enemy_index: int) -> None:
        for border_cell in self.e_incoming[enemy_index][1]:
            attack, plan = self.plans[border_cell]
            for p in plan:
                if p != enemy_index:
                    self.e_incoming[p][0] -= attack
                    self.e_incoming[p][1].remove(border_cell)
            self.move.add_transfer(Transfer(border_cell, enemy_index, attack))

    def add_plan(self, cell: int, enemies: List[EnemyCell], mass: int) -> None:
        pl = []
        for e in enemies:
            ei = e.index
            e_inc = self.e_incoming[ei]
            if e_inc[0] > -1:
                e_inc[0] += mass
                e_inc[1].append(cell)
                pl.append(ei)

        self.plans[cell] = (
            mass,
            pl,
        )

    def get_inside_available_mass(self, i_index: int, cell: int) -> int:
        return min(
            self.masses[cell] + self.incoming[cell] - CellType.MAXIMAL.min_size
            if i_index < self.first_border_nb
            else CellType.get_mass_over_min_size(
                self.masses[cell] + self.incoming[cell]
            ),
            self.masses[cell] - 1,
        )

    def get_needing_inside_available_mass(self, cell: int) -> int:
        return min(
            CellType.get_mass_over_min_size(
                self.masses[cell] + self.incoming[cell]
            ),
            self.masses[cell] - 1,
        )

    def ally_weight(self, cell: int) -> int:
        enemies = self.enemies[cell]
        needs, incoming = self.needs[cell], self.incoming[cell]
        if enemies:
            w = 3
            ep, _ = enemies
        else:
            w = 0
            ep = False

        if needs > incoming:
            if ep:
                w += 4
            else:
                w += 3
        else:
            mass = self.masses[cell]
            if needs - incoming <= mass - 1:
                w += 2
            else:
                w += 1
        return w

    def process_insides(self) -> None:
        for i, ci in enumerate(self.insides):
            self.needs[ci] = 0
            available_mass = self.get_inside_available_mass(i, ci)
            if available_mass < 0:
                needing_only = True
                available_mass = self.get_needing_inside_available_mass(ci)
            else:
                needing_only = False

            if available_mass <= 0:
                continue

            weight, needing = max(
                ((self.ally_weight(ni), ni) for ni in self.graph[ci]),
                key=self.need_key,
                default=None,
            )
            if needing_only and weight < 3:
                continue
            self.move.add_transfer(Transfer(ci, needing, available_mass))

    def process_border_cell(
        self, cell: int, enemy: bool, enemies: List[EnemyCell]
    ) -> None:
        available_mass = self.masses[cell] - 1

        if enemy:
            needed_defense = (
                self.needs[cell]
                - CellType.MAXIMAL.min_size
                - self.incoming[cell]
            )
            available_attack_mass = available_mass - needed_defense

        can_plan = False
        cp_index = 0
        for index_in_enemies in range(len(enemies)):
            min_attack, ei, def_need = astuple(enemies[index_in_enemies])
            inc_attack, _ = self.e_incoming[ei]
            if inc_attack <= -1:
                cp_index += 1
                continue
            available_attack = inc_attack + available_mass

            if min_attack > available_attack:
                can_plan = index_in_enemies == cp_index
                break
            if (
                enemy
                and min_attack > available_attack_mass + inc_attack + def_need
            ):
                break

            self.e_incoming[ei][0] = -1
            if inc_attack > 0:
                self.execute_plans(ei)
                min_attack -= inc_attack

            available_mass -= min_attack
            if enemy:
                available_mass = min(
                    available_mass,
                    available_attack_mass - min_attack + def_need,
                )
            else:
                available_mass += self.incoming[cell]
            available_mass = min(
                self.masses[cell] - 1 - min_attack, available_mass
            )
            attack = min_attack + CellType.get_mass_over_min_size(
                available_mass
            )
            self.move.add_transfer(
                Transfer(
                    cell,
                    ei,
                    attack,
                )
            )
            return
        _, needing = max(
            (
                (self.needs[ni] - self.incoming[ni], ni)
                for ni in self.graph[cell]
                if self.enemies[ni][0] and self.needs[ni] > self.incoming[ni]
            ),
            key=self.key,
            default=(None, None),
        )
        if can_plan:
            if enemy or not needing:
                self.add_plan(cell, enemies, available_mass)
            return

        attack = min(
            CellType.get_mass_over_min_size(
                available_mass + self.incoming[cell]
            ),
            available_mass,
        )
        if attack > 0:
            self.move.add_transfer(
                Transfer(
                    cell,
                    needing if needing else enemies[len(enemies) - 1].index,
                    attack,
                )
            )

    def get_move(self, game: Game) -> List[Transfer]:
        self.move = TransferMove()
        self.game = game
        self.process_game(game)

        self.process_insides()

        # border cells
        for cell in self.border:
            enemies_player, enemies_neutral = self.enemies[cell]
            if enemies_player:
                self.process_border_cell(
                    cell,
                    self.me == 1,
                    sorted(enemies_player, key=self.enemy_key),
                )
            else:
                self.process_border_cell(
                    cell, False, sorted(enemies_neutral, key=self.enemy_key)
                )
        return TransferMove.get_transfers_i(self.move)
