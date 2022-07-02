#!/usr/bin/env python3
from random import Random
from typing import Tuple, List, Union, Iterable, Optional
from math import sqrt, ceil
import game.cells as gc
from dataclasses import dataclass


def half_counts_of_cells_in_columns(
    num_cells, d_inc: int, width, half_width, est_height, rnd: Random
) -> List[int]:
    """Return number of cells in columns for the first half (symmetric) of grid and height."""
    # process odd x even
    if num_cells % 2 == 1 and est_height % 2 == 0:
        est_height += 1
    mid = est_height // max(1, d_inc // 2)
    # mid has to be odd if num_cells is odd
    if num_cells % 2 == 1 and mid % 2 != 1:
        mid += 1
    elif num_cells % 2 == 0 and mid % 2 == 1:
        mid -= 1

    avg_count = (num_cells - mid) // (width - 1)
    max_count, min_count = min(avg_count * 5 // 2, est_height), max(
        1, avg_count // 2
    )
    # raw counts
    counts = rnd.choices(range(min_count, max_count), k=half_width)
    # missing in counts sum
    half_missing = (num_cells - mid) // 2 - sum(counts)
    if half_missing != 0:
        # add/remove missing counts
        # get order
        idcs = rnd.sample(range(len(counts)), k=len(counts))
        if half_missing > 0:
            get_dif = lambda count, half_missing: min(
                max_count - count, half_missing
            )
        else:
            get_dif = lambda count, half_missing: max(
                min_count - count, half_missing
            )
        for i in idcs:
            if half_missing == 0:
                break
            dif = get_dif(counts[i], half_missing)
            counts[i] += dif
            half_missing -= dif
    # add middle column count
    counts.append(mid)
    return counts, est_height


@dataclass
class HoleCell:
    vertical_hole: bool = False  # False for edge
    horizontal_hole: bool = False  # False for edge


def add_neighbors(
    cells: Iterable["gc.Cell"], neighbors: Iterable["gc.Cell"]
) -> None:
    for c, n in zip(cells, neighbors):
        assert n not in c.neighbors
        c.neighbors.append(n)
        assert c not in n.neighbors
        n.neighbors.append(c)


@dataclass
class Neighbor:
    cells: tuple["gc.Cell"]  # mirror cells
    hole_weight: int = 0


def get_grid_and_positions(
    width,
    height,
    hole_probability,
    rnd: Random,
    counts: List[int],
    middle: int,
    cell_iterator,
    reverse_cell_iterator,
) -> Tuple[List[List[Optional["gc.Cell"]]], List[Tuple[int, int]]]:
    """
    Return grid with cells or None and positions of the cells.
    """
    grid = [[None] * height for _ in range(width)]
    positions = []
    positions2 = []

    w, h = width - 1, height - 1

    def add_cells(x, y, cells):
        nonlocal grid, positions, positions2, w, h
        positions.append((x, y))
        positions2.append((w - x, h - y))
        grid[x][y] = cells[0]
        grid[w - x][h - y] = cells[1]

    def update_neighbors_with_hole(nbs: Iterable[Neighbor]):
        nonlocal rnd, hole_probability
        for n in nbs:
            if n is not None:
                if rnd.random() < hole_probability:
                    n.hole_weight -= 1
                else:
                    n.hole_weight += 1

    def add_hv_neighbors(cells, nbs: Iterable[Neighbor]):
        for n in nbs:
            if n is not None and n.hole_weight >= 0:
                add_neighbors(cells, n.cells)

    horizontal_neighbors: list[Neighbor] = []
    vertical_neighbor: Neighbor = None

    # fist column without holes
    cell_count = counts[0]
    holes = [False] * cell_count + [True] * (height - cell_count)
    rnd.shuffle(holes)
    for y, hole in enumerate(holes):
        if hole:
            horizontal_neighbors.append(None)
            continue
        cells = (next(cell_iterator), next(reverse_cell_iterator))
        add_cells(0, y, cells)
        horizontal_neighbors.append(Neighbor(cells))
        add_hv_neighbors(cells, (vertical_neighbor,))
        vertical_neighbor = Neighbor(cells)

    # columns
    for x, cell_count in enumerate(counts[1:-1], start=1):
        vertical_neighbor = None
        holes = [False] * cell_count + [True] * (height - cell_count)
        rnd.shuffle(holes)
        for y, hole in enumerate(holes):
            horizontal_neighbor = horizontal_neighbors[y]
            if hole:
                update_neighbors_with_hole(
                    (vertical_neighbor, horizontal_neighbor)
                )
                continue

            cells = (next(cell_iterator), next(reverse_cell_iterator))
            add_cells(x, y, cells)
            add_hv_neighbors(cells, (vertical_neighbor, horizontal_neighbor))
            vertical_neighbor = Neighbor(cells)
            horizontal_neighbors[y] = Neighbor(cells)

    # middle column symmetric
    cell_count = counts[-1]
    vertical_neighbor = None
    holes = [False] * (cell_count // 2) + [True] * (
        height // 2 - cell_count // 2
    )
    rnd.shuffle(holes)
    # center tile
    if height % 2:
        if cell_count % 2:
            holes += [None]
        else:
            holes += [True]
    for y, hole in enumerate(holes):
        horizontal_neighbor1 = horizontal_neighbors[y]
        horizontal_neighbor2 = horizontal_neighbors[h - y]
        # middle mirror
        if horizontal_neighbor2 is not None:
            horizontal_neighbor2.cells = horizontal_neighbor2.cells[::-1]
        if hole:
            # connect from symmetric other half
            if (
                horizontal_neighbor1 is not None
                and horizontal_neighbor2 is not None
            ):
                weight = (
                    horizontal_neighbor1.hole_weight
                    + horizontal_neighbor2.hole_weight
                )
                if rnd.random() < hole_probability:
                    weight -= 1
                else:
                    weight += 1
                if weight >= 0:
                    # middle hole
                    if horizontal_neighbor1 is horizontal_neighbor2:
                        add_neighbors(
                            (horizontal_neighbor1.cells[0],),
                            (horizontal_neighbor1.cells[1],),
                        )
                    else:
                        add_neighbors(
                            horizontal_neighbor1.cells,
                            horizontal_neighbor2.cells,
                        )
            update_neighbors_with_hole((vertical_neighbor,))
            continue
        if hole is None:
            cells = (next(cell_iterator),) * 2
            positions.append((middle, y))
            grid[middle][y] = cells[0]
            horizontal_neighbor2 = None
        else:
            cells = (next(cell_iterator), next(reverse_cell_iterator))
            add_cells(middle, y, cells)
        add_hv_neighbors(
            cells,
            (vertical_neighbor, horizontal_neighbor1, horizontal_neighbor2),
        )
        vertical_neighbor = Neighbor(cells)
    positions.extend(reversed(positions2))
    return grid, positions


@dataclass
class Component:
    cells: list["gc.Cell"]
    indices: set[int]


def get_components(cells) -> tuple[list[Component], dict[int, Component]]:
    """Find components by dfs."""
    all_components = []
    cell_to_comp = {}

    active = []
    active_set = set()
    comp = Component(active, active_set)
    done = set()
    for c in cells:
        if c.index in done:
            continue
        queue = [c]
        while queue:
            c = queue.pop()
            if c.index in done:
                continue
            done.add(c.index)
            active.append(c)
            active_set.add(c.index)
            cell_to_comp[c.index] = comp
            for nb in c.neighbors:
                if nb.index in done:
                    continue
                else:
                    queue.append(nb)
        all_components.append(comp)
        active, active_set = [], set()
        comp = Component(active, active_set)
    return all_components, cell_to_comp


def connect_components(
    cells: List["gc.Cell"],
    rnd: Random,
    positions: List[Tuple[int, int]],
    grid: List[List[Optional["gc.Cell"]]],
    fail: bool = True,
) -> bool:
    """
    Try to connect all components.
    If fail return on fail otherwise try to connect as many components as you can.
    """
    width, height = len(grid), len(grid[0])
    all_components, cell_to_comp = get_components(cells)
    if len(all_components) == 1:
        return True

    def connect_components(
        comps: Iterable[Component],
        other_comps: Iterable[Component],
    ) -> None:
        nonlocal cell_to_comp
        for comp, o_comp in zip(comps, other_comps):
            o_comp.cells.extend(comp.cells)
            o_comp.indices.update(comp.indices)
            for i in comp.indices:
                cell_to_comp[i] = o_comp

    while len(all_components) > 1:
        # larger in the front
        all_components.sort(key=lambda comp: len(comp.cells), reverse=True)
        if fail:
            # connect only owned components
            comp = cell_to_comp[0]
            all_components.remove(comp)
        else:
            # all should be connected, start with smaller
            comp = all_components.pop()
        rnd.shuffle(comp.cells)

        # find cell in other component searching in direction as long as possible
        # if other cell from the same component is found
        #  set it as active and continue in the same direction
        found = False
        comp_cells = {
            c.index: [(0, 1), (0, -1), (1, 0), (-1, 0)] for c in comp.cells
        }
        while comp_cells:
            cell_index, dirs = comp_cells.popitem()
            while dirs:
                dir = dirs.pop(rnd.randrange(len(dirs)))
                dx, dy = dir
                ax, ay = positions[cell_index]  # active_cell position
                fx, fy = ax, ay  # found_cell position
                active_cell_i = cell_index
                while True:
                    fx += dx
                    fy += dy
                    if not (0 <= fx < width and 0 <= fy < height):
                        break
                    found_cell = grid[fx][fy]
                    if found_cell is None:
                        continue
                    if found_cell.index in comp.indices:
                        if (
                            found_cell.index in comp_cells
                            and dir in comp_cells[found_cell.index]
                        ):
                            active_cell_i = found_cell.index
                            comp_cells[active_cell_i].remove(dir)
                            ax, ay = fx, fy
                        continue
                    found = True
                    break
                if found:
                    break
            if found:
                break
        if not found:
            return not fail

        active_cell = cells[active_cell_i]

        # process mirror active cell
        ax2, ay2 = width - 1 - ax, height - 1 - ay
        active_mirror = grid[ax2][ay2]
        if active_mirror is active_cell:
            cells1 = (active_cell,) * 2
            comps1 = (comp,)
        else:
            if found_cell is active_mirror:
                add_neighbors((active_cell,), (found_cell,))
                other_comp = cell_to_comp[found_cell.index]
                connect_components((comp,), (other_comp,))
                continue

            cells1 = (active_cell, active_mirror)

            if active_mirror.index in comp.indices:
                # active mirror is in the same component
                comps1 = (comp,)
            else:
                other_comp = cell_to_comp[active_mirror.index]
                if found_cell.index in other_comp.indices:
                    # found cell in the same component as active_mirror
                    comps1 = (comp,)
                else:
                    all_components.remove(other_comp)
                    comps1 = (
                        comp,
                        other_comp,
                    )

        # process mirror found cell and connect components
        fx2, fy2 = width - 1 - fx, height - 1 - fy
        found_mirror = grid[fx2][fy2]

        if (
            found_cell is found_mirror
            or found_mirror.index in comps1[0].indices
            or (len(comps1) > 1 and found_mirror.index in comps1[1].indices)
        ):
            # found cells are in the same component
            if found_cell is found_mirror and cells1[0] is cells1[1]:
                add_neighbors(cells1, (found_cell,))
            else:
                add_neighbors(cells1, (found_cell, found_mirror))
            other_comp = cell_to_comp[found_cell.index]
            connect_components(comps1, (other_comp,) * 2)
        else:
            add_neighbors(cells1, (found_cell, found_mirror))
            other_comp1 = cell_to_comp[found_cell.index]
            other_comp2 = cell_to_comp[found_mirror.index]
            if len(comps1) == 1:
                # mirror in same comp, or mirror in found comp
                if other_comp1 is not other_comp2:
                    all_components.remove(other_comp2)
                    comps1 += (other_comp2,)
                connect_components(comps1, (other_comp1,) * 2)
            else:
                connect_components(comps1, (other_comp1, other_comp2))
    return True


def generate_cells(
    num_cells: int,
    rnd: Random,
    density: float = 0.5,
    hole_probability: float = 0.6,
) -> Tuple[
    List["gc.Cell"],
    List[int],
    Tuple[List[int], List[int], List[int]],
    List[int],
    List[List[int]],
    List[Tuple[int, int]],
    Tuple[int, int],
]:
    """
    Generate cells and set their neighbors.
    Cells will be centrally symmetrical.

    Returns:
    * list of all cells. Cells are completely initialized.
    * list of cell owners
    * starting positions for (neutral, player1, player2)
    * total_masses for all (neutral, player1, player2)
    * list of lists of neighboring cells indices
    * list of cell positions
    * grid size
    """
    assert 0.2 <= density <= 1
    assert 0 <= hole_probability <= 1
    # increase in height, etc.
    d_inc = int(1 / density)
    x = sqrt(num_cells * d_inc / 40)
    half_width = ceil(4 * x)
    width, estimated_height = half_width * 2 + 1, ceil(5 * x)

    # try iterate to connect owned cells (for small density)
    # if it fails for the 9th time let it be and connect what you can
    for i in range(10):
        counts, height = half_counts_of_cells_in_columns(
            num_cells, d_inc, width, half_width, estimated_height, rnd
        )

        cells = [gc.Cell(i) for i in range(num_cells)]
        # set owner
        for c in cells[: counts[0]]:
            c.owner = 1
        for c in cells[-counts[0] :]:
            c.owner = 2

        grid, positions = get_grid_and_positions(
            width,
            height,
            hole_probability,
            rnd,
            counts,
            half_width,
            iter(cells),
            reversed(cells),
        )

        if connect_components(cells, rnd, positions, grid, i != 9):
            break
        # if it fails for the 10th time let it be and connect what you can

    owners = (
        [1] * counts[0] + [0] * (num_cells - counts[0] * 2) + [2] * counts[0]
    )
    total_armies = [
        (num_cells - counts[0] * 2) * gc.Cell.INITIAL_SIZE,
        counts[0] * gc.Cell.INITIAL_SIZE,
        counts[0] * gc.Cell.INITIAL_SIZE,
    ]

    neighbors = [[n.index for n in c.neighbors] for c in cells]

    starting_cell_indices = (
        list(range(counts[0], num_cells - counts[0])),
        list(range(counts[0])),
        list(range(num_cells - counts[0], num_cells)),
    )

    for c in cells:
        if c in c.neighbors:
            print(c.index, [n.index for n in c.neighbors])

    return (
        cells,
        owners,
        starting_cell_indices,
        total_armies,
        neighbors,
        positions,
        (width, height),
    )
