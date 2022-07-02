#!/usr/bin/env python3
from math import ceil, floor
from typing import List, Tuple, Union
from random import Random
from dataclasses import dataclass
from copy import deepcopy
from sys import stderr
import game.cell_generator


def ceil_div(a, b):
    return -1 * (-a // b)


@dataclass
class CellProperties:
    size_index: int
    growth: int
    min_size: int


def _get_cell_type_properties(TYPES) -> tuple[CellProperties]:
    return (None,) + sum(
        (
            (TYPES[i - 1],) * (TYPES[i].min_size - TYPES[i - 1].min_size)
            for i in range(1, len(TYPES))
        ),
        (),
    )


class CellType:
    """
    Utility static class for getting type of the cell.

    Note: Must be kept consistent.
    """

    NEUTRAL = CellProperties(-1, 1, 1)

    SMALL = CellProperties(0, 5, 1)
    MEDIUM = CellProperties(1, 12, 35)
    BIG = CellProperties(2, 35, 100)

    # NEEDS TO BE KEPT CONSISTENT
    TYPES = (SMALL, MEDIUM, BIG)

    # AUTO
    MINIMAL = TYPES[0]
    MAXIMAL = TYPES[-1]
    MAX_I = MAXIMAL.min_size
    PROPERTIES = _get_cell_type_properties(TYPES)

    @classmethod
    def get_type(cls, mass: int) -> CellProperties:
        if mass >= cls.MAX_I:
            return cls.MAXIMAL
        return cls.PROPERTIES[mass]

    @classmethod
    def get_type_index(cls, mass: int) -> int:
        if mass >= cls.MAX_I:
            return cls.MAXIMAL.size_index
        return cls.PROPERTIES[mass].size_index

    @classmethod
    def get_growth(cls, mass: int) -> int:
        if mass >= cls.MAX_I:
            return cls.MAXIMAL.growth
        return cls.PROPERTIES[mass].growth

    @classmethod
    def get_mass_over_min_size(cls, mass: int, size_index: int = -1) -> int:
        """
        Return mass available for transfer stay in current or specified size class.

        Note: Result can be negative.
        Note2: For mass < 1 returns 0.
        """
        if mass <= 1:
            return 0
        if size_index == -1:
            if mass >= cls.MAX_I:
                return mass - cls.MAXIMAL.min_size
            return mass - cls.PROPERTIES[mass].min_size
        else:
            return mass - cls.TYPES[size_index].min_size


class Cell:
    INITIAL_SIZE = 10
    SIZE_CAP = 350

    WHEN_SAFE_GROWTH_PER_NEIGHBOR = 10
    OVER_CAP_DECAY = 5

    MAX_GROWTH = CellType.MAXIMAL.growth
    NEUTRAL_GROWTH = CellType.NEUTRAL.growth

    def __init__(self, index: int, owner: int = 0):
        self.mass: int = Cell.INITIAL_SIZE
        self.neighbors: List["Cell"] = []
        self.index: int = index
        self.owner: int = owner

    def __eq__(self, __o: object) -> bool:
        if self is __o:
            return True
        if isinstance(__o, int):
            return self.index == __o
        elif isinstance(__o, Cell):
            return self.index == __o.index

    @property
    def size_index(self) -> int:
        return CellType.get_type(self.mass).size_index

    @property
    def type(self) -> CellType:
        return CellType.get_type(self.mass)

    @classmethod
    def get_growth(cls, mass: int, owner: int, safe: int) -> int:
        """
        Return growth of the cell with given mass, owner
        and information whether all neighboring cells are of the same owner
        as their number (0 for not safe).
        """
        if mass > cls.SIZE_CAP:
            loss = ceil_div(mass, cls.OVER_CAP_DECAY)
            growth = cls.MAX_GROWTH - loss
        elif owner == 0:
            growth = cls.NEUTRAL_GROWTH
        else:
            growth = (
                CellType.get_growth(mass)
                + safe * cls.WHEN_SAFE_GROWTH_PER_NEIGHBOR
            )
        return growth

    def grow(self) -> int:
        """
        Grows the cell with respect to current size class
            and to the owner of neighboring cells.

        Return the difference in mass.
        """
        if self.mass > self.SIZE_CAP:
            loss = ceil_div(self.mass, self.OVER_CAP_DECAY)
            growth = self.MAX_GROWTH - loss
        elif self.owner == 0:
            growth = self.NEUTRAL_GROWTH
        else:
            growth = CellType.get_growth(self.mass)

            # safety check
            if all(self.owner == n.owner for n in self.neighbors):
                growth += (
                    len(self.neighbors) * self.WHEN_SAFE_GROWTH_PER_NEIGHBOR
                )

        self.mass += growth
        return growth


@dataclass
class Transfer:
    """
    Representation of single transfer.

    List of Transfers form one game move.

    Source and target can be cell or cell index,
    but move must contain only indices — you can use
    TransferMove.get_transfers_i.
    """

    source: Union[int, Cell]
    target: Union[int, Cell]
    mass: int


class TransferMove:
    """Utility class for creating moves."""

    def __init__(self, transfers: List[Transfer] = None) -> None:
        self.transfers: List[Transfer] = [] if transfers is None else transfers

    def add_transfer(self, transfer: Transfer) -> None:
        self.transfers.append(transfer)

    def add_and_combine_transfer(self, transfer: Transfer) -> None:
        s, t, m = transfer.source, transfer.target, transfer.mass
        for tr in reversed(self.transfers):
            if tr.source == s and tr.target == t:
                tr.mass += m
                return
        self.transfers.append(transfer)

    def get_transfers(self) -> List[Transfer]:
        return self.transfers

    @staticmethod
    def get_transfers_i(
        move: Union["TransferMove", List[Transfer]]
    ) -> List[Transfer]:
        """Converts transfers with cell class representations to index representations."""
        if isinstance(move, TransferMove):
            move = move.get_transfers()
        return [
            Transfer(
                t.source if isinstance(t.source, int) else t.source.index,
                t.target if isinstance(t.target, int) else t.target.index,
                t.mass,
            )
            for t in move
        ]


class Game:
    """
    Cell Wars game-state representation.

    Note you can disable usage of cell class representation by setting
    'use_cells' to False.

    Useful methods:
    - clone
    - sizes
    - get_player_cells
    - get_cell
    - attack
    - is_neighbor
    - get_owner
    - is_owned_by
    - total_mass
    - cells_owned
    - current_player
    - is_done
    - borders_enemy_cells
    - round

    Methods for advancing the game:
    - make_move
    - grow_cells
    """

    ATTACK_MUL = 0.8
    DEF_ATTACK_MUL = 0.8
    SUC_DEFENSE_MUL = 0.9

    def __init__(self, seed: int = None, max_rounds: int = -1) -> None:
        self.winner: int = -1
        self.counter: int = -1
        self.turn: int = -1
        self.max_rounds: int = max_rounds * 2
        self.random: Random = Random(seed)
        self.num_cells: int = -1

        self.cells: List[Cell] = None
        self.masses: List[int] = None
        self.owners: List[int] = None
        self.total_masses: List[int] = None
        self.neighbors: List[List[int]] = None
        self.starting_indices: Tuple[List[int], List[int], List[int]] = None

        # defines whether instance of game should
        # touch self.cells at all (even for cloning).
        self.use_cells = True

    def new_game(
        self,
        num_cells: int,
        density: float = None,
        hole_probability: float = None,
        gui=None,
    ) -> None:
        self.winner = -1
        self.counter = 0
        self.turn = 1
        if num_cells is not None:
            self.num_cells = num_cells
        self._init_cells_and_gui(density, hole_probability, gui)

    @property
    def sizes(self) -> List[int]:
        """Return list of size indices."""
        return [CellType.get_type(mass).size_index for mass in self.masses]

    def get_gui_info(self) -> Tuple[List[int], List[int], List[int], List[int]]:
        """Owners, masses, sizes_i, total_masses."""
        return (
            self.owners,
            self.masses,
            self.sizes,
            self.total_masses,
            self.round,
        )

    def _init_cells_and_gui(
        self, density: float = None, hole_probability: float = None, gui=None
    ) -> None:
        (
            self.cells,
            self.owners,
            self.starting_indices,
            self.total_masses,
            self.neighbors,
            positions,
            grid_size,
        ) = game.cell_generator.generate_cells(
            self.num_cells, self.random, density, hole_probability
        )
        self.masses = [c.mass for c in self.cells]
        if gui is not None:
            gui.init_cells(grid_size, positions, self.neighbors)

    def clone(self) -> "Game":
        ret = Game()
        ret.turn = self.turn
        ret.winner = self.winner
        ret.counter = self.counter
        ret.max_rounds = self.max_rounds

        ret.num_cells = self.num_cells
        ret.use_cells = self.use_cells
        if self.use_cells:
            # preserves cell neighbors references
            ret.cells = deepcopy(self.cells)
        ret.owners = [*self.owners]
        ret.masses = [*self.masses]
        ret.total_masses = [*self.total_masses]
        ret.neighbors = [[*nbs] for nbs in self.neighbors]
        ret.starting_indices = tuple([*sis] for sis in self.starting_indices)
        return ret

    def get_player_cells(
        self, player: int, *, return_cells: bool = True
    ) -> Union[List[int], List[Cell]]:
        """Return cells or indices of cells that are controlled by given player."""
        indices = [i for i, o in enumerate(self.owners) if o == player]

        if return_cells and self.use_cells:
            return [self.cells[i] for i in indices]
        else:
            return indices

    def get_player_starting_cells(
        self, player: int, *, return_cells: bool = True
    ) -> Union[List[int], List[Cell]]:
        """
        Return cells or indices of cells
        that are controlled by given player at the beginning of the game.
        """
        indices = self.starting_indices[player]

        if return_cells and self.use_cells:
            return [self.cells[i] for i in indices]
        else:
            return indices

    def get_cell(self, index: int) -> Cell:
        return self.cells[index]

    def grow_cells(self) -> None:
        """Add mass to all cells with respect to their size and neighbors."""
        growths = [0, 0, 0]
        if self.use_cells:
            for ci, (c, o) in enumerate(zip(self.cells, self.owners)):
                g = c.grow()
                growths[o] += g
                self.masses[ci] += g
        else:
            ows = self.owners
            nbs = self.neighbors
            for ci, (mass, o) in enumerate(zip(self.masses, self.owners)):
                s = 0
                if o != 0 and all(ows[n] == o for n in nbs[ci]):
                    s = len(nbs[ci])
                g = Cell.get_growth(mass, o, s)
                growths[o] += g
                self.masses[ci] += g
        for i in range(len(growths)):
            self.total_masses[i] += growths[i]

    @staticmethod
    def attack(attacking: int, defending: int) -> Tuple[bool, int]:
        """Return whether attack is successful and new mass of attacking cell."""
        # TODO randomize
        attacking = attacking * Game.ATTACK_MUL
        if defending >= attacking:
            return False, ceil(defending - attacking * Game.DEF_ATTACK_MUL)
        return True, max(1, floor(attacking - defending * Game.SUC_DEFENSE_MUL))

    def cell_can_send_mass(
        self, mass: int, source_i: int, recipient_i: int
    ) -> Tuple[bool, str]:
        """
        Checks whether cell can send given mass to given cell.
        Return if possible and error reason.

        Does not test multiple transfers.

        Can fail if:
            remaining mass is 0 or less
            recipient is not neighbor
        """
        if self.masses[source_i] <= mass:
            return False, "source has not enough mass"
        if recipient_i not in self.neighbors[source_i]:
            return (
                False,
                "recipient is not neighbor of source",
            )
        return True, None

    def print_transfer_error(
        self, source: int, target: int, mass: int, errors: List[str]
    ) -> None:
        print(
            "Transfer {}:{} -> {} declined, turn {}.\nCause: {}".format(
                source, mass, target, self.counter, ", ".join(errors)
            ),
            file=stderr,
        )

    def _transfer(self, cell_transfers: List[Transfer]) -> None:
        update_cells = self.use_cells
        outgoing = [0] * self.num_cells
        transfers = [0] * self.num_cells
        attacks = [0] * self.num_cells
        real_sender = self.turn
        done = [False] * self.num_cells

        for tr in cell_transfers:
            si, ti, mass = tr.source, tr.target, tr.mass
            # check validity
            errors = []
            if mass <= 0:
                errors.append("non positive mass")
            if done[si]:
                errors.append("source has already transferred")
            if si == ti:
                errors.append("source targets itself")
            sender = self.owners[si]
            if sender != real_sender:
                errors.append("source is not owned")
            possible, error = self.cell_can_send_mass(
                outgoing[si] + mass, si, ti
            )
            if not possible:
                errors.append(error)

            if errors:
                self.print_transfer_error(si, ti, mass, errors)
                continue

            # append to perform
            done[si] = True
            outgoing[si] += mass
            recipient = self.owners[ti]
            if sender == recipient:
                transfers[ti] += mass
            else:
                attacks[ti] += mass

        # remove transferred mass
        if update_cells:
            for c, t, o in zip(self.cells, transfers, outgoing):
                if t > 0 or o > 0:
                    c.mass += t - o
                    self.masses[c.index] += t - o
        else:
            for i, (t, o) in enumerate(zip(transfers, outgoing)):
                self.masses[i] += t - o

        # receive mass
        total_difs = [0, 0, 0]
        # transfers only as a placeholder
        for si, (c, mass) in enumerate(
            zip(self.cells if update_cells else transfers, attacks)
        ):
            if mass == 0:
                continue
            prior_mass = self.masses[si]
            recipient = self.owners[si]
            success, remaining_mass = Game.attack(mass, prior_mass)
            if success:
                self.owners[si] = real_sender
                total_difs[real_sender] -= mass - remaining_mass
                if update_cells:
                    if c.owner == 0:
                        c.neutral = False
                    c.owner = real_sender
                total_difs[recipient] -= prior_mass
            else:
                total_difs[sender] -= mass
                total_difs[recipient] -= prior_mass - remaining_mass
            if update_cells:
                c.mass = remaining_mass
            self.masses[si] = remaining_mass

        for i in range(3):
            self.total_masses[i] += total_difs[i]

    def is_neighbor(self, cell_index1: int, cell_index2: int) -> bool:
        """Whether cells with given indices are neighbors."""
        return cell_index2 in self.neighbors[cell_index1]

    def get_owner(self, cell: Union[int, Cell]) -> int:
        """Return player owning given cell or cell with given index."""
        if isinstance(cell, Cell):
            cell = cell.index
        return self.owners[cell]

    def is_owned_by(self, cell: Union[int, Cell], player: int) -> bool:
        """Whether given cell/index is owned by given player."""
        if isinstance(cell, Cell):
            cell = cell.index
        return self.owners[cell] == player

    def total_mass(self, player: int) -> int:
        """Return total mass of cells given player own."""
        return self.total_masses[player]

    def cells_owned(self, player: int) -> int:
        """Return number of cells given player own."""
        return sum(o == player for o in self.owners)

    @property
    def current_player(self) -> int:
        return self.turn

    def is_done(self) -> bool:
        return self.winner != -1

    def borders_enemy_cells(
        self, cell: Union[int, Cell], for_player: int
    ) -> bool:
        """Whether given cell/index has neighbor with different owner."""
        if isinstance(cell, Cell):
            cell = cell.index
        return any(for_player != self.owners[n] for n in self.neighbors[cell])

    @property
    def round(self):
        return self.counter // 2

    def get_player_round(self, p: int) -> int:
        if p == 1:
            return ceil_div(self.counter, 2)
        else:
            return self.counter // 2

    def make_move(self, move: List[Tuple[int, int, int]]) -> None:
        self._transfer(move)

        self.counter += 1
        if self.total_masses[1] == 0:
            self.winner = 2
        elif self.total_masses[2] == 0:
            self.winner = 1
        elif self.counter == self.max_rounds:
            self.winner = 0

        self.turn = 3 - self.turn
