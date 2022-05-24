from random import Random
from typing import Tuple, List, Union, Iterable, Optional
from math import sqrt, ceil
import game.cells as gc


def half_counts_of_cells_in_columns(
    num_cells, d_inc: int, width, half_width, height, rnd: Random
) -> List[int]:
    """Return number of cells in columns for the first half of grid."""
    mid = height // max(1, d_inc // 2)
    if num_cells % 2 == 1 and mid % 2 != 1:
        height += 1
        mid += 1
    elif num_cells % 2 == 0 and mid % 2 == 1:
        mid -= 1
    avg_count = num_cells // width
    max_count, min_count = min(avg_count * 5 // 2, height), max(
        1, avg_count // 2
    )
    counts = rnd.choices(range(min_count, max_count), k=half_width)
    half_missing = (num_cells - mid) // 2 - sum(counts)
    if half_missing != 0:
        idcs = rnd.sample(range(len(counts)), k=len(counts))
        if half_missing > 0:
            for i in idcs:
                if half_missing == 0:
                    break
                dif = min(max_count - counts[i], half_missing)
                counts[i] += dif
                half_missing -= dif
        else:
            for i in idcs:
                if half_missing == 0:
                    break
                dif = max(min_count - counts[i], half_missing)
                counts[i] += dif
                half_missing -= dif
    counts.append(mid)
    return counts


def get_grid_with_holes(
    width, height, hole_probability, rnd: Random, counts: List[int], middle: int
) -> List[List[Union[bool, Tuple[bool, bool]]]]:
    """
    Grid cell is True for Cell, (True/False, True/False) for hole, where True means, there should not be edge through in (horizontal, vertical) direction.
    Edges through multiple holes are decide by majority with, tie - edge.
    """
    grid = [[True] * height for _ in range(width)]
    mid_col = grid[middle]

    def rnd_to_hole(rand) -> Tuple[Union[None, bool], Union[None, bool]]:
        return tuple(True if r < hole_probability else False for r in rand)

    rh = range(height)
    for x, (col, hole_count) in enumerate(
        zip(grid[:middle], (height - count for count in counts[:-1]))
    ):
        rem = rnd.sample(rh, k=hole_count)
        if x != 0:
            rands = ((rnd.random(), rnd.random()) for _ in range(hole_count))
            holes = map(rnd_to_hole, rands)
        else:
            holes = ((False, False) for _ in range(hole_count))
        for i, hole in zip(rem, holes):
            col[i] = hole
    hole_count = height - counts[-1]
    if hole_count % 2 != 0:
        mid_col[height // 2] = (False, False)
    rem = rnd.sample(range(height // 2), k=hole_count // 2)
    rands = ((rnd.random(), rnd.random()) for _ in range(hole_count // 2))
    holes = map(rnd_to_hole, rands)
    for i, hole in zip(rem, holes):
        mid_col[i] = hole
        mid_col[height - i - 1] = hole
    return grid


def add_neighbors(
    cells: Iterable["gc.Cell"], neighbors: Iterable["gc.Cell"]
) -> None:
    for c, n in zip(cells, neighbors):
        c.neighbors.append(n)
        n.neighbors.append(c)


def set_neighbors_update_grid_get_positions(
    num_cells,
    cells: List["gc.Cell"],
    grid: List[List[Union[bool, Tuple[bool, bool]]]],
    middle,
) -> List[Tuple[int, int]]:
    """
    Sets neighbors in cells, grid is changed to List[List[Optional[Cell]]].
    Returns positions of cells.
    """
    width, height = len(grid), len(grid[0])
    positions = []
    positions2 = []
    i = 0
    last_cell_i = num_cells - 1
    w, h = width - 1, height - 1
    last_horizontal_neighbors = [None] * height
    for x, col in enumerate(grid[:middle]):
        last_vertical_neighbors = None
        for y, c in enumerate(col):
            h_nb = last_horizontal_neighbors[y]
            v_nb = last_vertical_neighbors
            if c is not True:
                col[y] = None
                grid[width - 1 - x][height - 1 - y] = None
                h_hole, v_hole = c
                if h_nb is not None:
                    if h_hole:
                        h_nb[1] -= 1
                    else:
                        h_nb[1] += 1
                if v_nb is not None:
                    if v_hole:
                        v_nb[1] -= 1
                    else:
                        v_nb[1] += 1
                continue
            col[y] = cells[i]
            grid[width - 1 - x][height - 1 - y] = cells[last_cell_i - i]
            a_cells = (cells[i], cells[last_cell_i - i])
            positions.append((x, y))
            positions2.append((w - x, h - y))
            i += 1
            if v_nb is not None and v_nb[1] >= 0:
                add_neighbors(a_cells, v_nb[0])
            last_vertical_neighbors = [a_cells, 0]
            if h_nb is not None and h_nb[1] >= 0:
                add_neighbors(a_cells, h_nb[0])
            last_horizontal_neighbors[y] = [a_cells, 0]

    mid_col = grid[middle]
    last_vertical_neighbor = None
    for y, c in enumerate(mid_col):
        v_nb = last_vertical_neighbor
        h_nb = last_horizontal_neighbors[y]
        horizontal_neighbors = []
        if h_nb is not None:
            horizontal_neighbors.append((h_nb[0][0], h_nb[1]))
        h_nb2 = last_horizontal_neighbors[height - 1 - y]
        if h_nb2 is not None:
            horizontal_neighbors.append((h_nb2[0][1], h_nb2[1]))
        if c is not True:
            mid_col[y] = None
            h_hole, v_hole = c
            if len(horizontal_neighbors) > 1:
                h_sum = sum(hnb[1] for hnb in horizontal_neighbors)
                if h_hole:
                    h_sum -= 1
                else:
                    h_sum += 1
                if h_sum >= 0:
                    add_neighbors(
                        (horizontal_neighbors[0][0],),
                        (horizontal_neighbors[1][0],),
                    )
            if v_nb is not None:
                if v_hole:
                    v_nb[1] -= 1
                else:
                    v_nb[1] += 1
            continue
        mid_col[y] = cells[i]
        cell = (cells[i],)
        positions.append((middle, y))
        i += 1
        if v_nb is not None and v_nb[1] >= 0:
            add_neighbors(cell, v_nb[0])
        last_vertical_neighbor = [cell, 0]
        for nb, h_sum in horizontal_neighbors:
            if h_sum >= 0:
                add_neighbors(cell, (nb,))

    positions.extend(reversed(positions2))
    return positions


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
    all_components = []

    def find_component_index(cell_index) -> int:
        return next(
            (i for i, (oc, _) in enumerate(all_components) if cell_index in oc)
        )

    def connect_components(
        comps: Iterable[Tuple[List["gc.Cell"]]],
        indices_of_other_components: Iterable[int],
    ) -> None:
        """comps are tuples (list of cells, set of cell indices)"""
        for (comp, c_set), oci in zip(comps, indices_of_other_components):
            all_components[oci][0].extend(comp)
            all_components[oci][1].update(c_set)

    # find components by dfs
    active = []
    active_set = set()
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
            for nb in c.neighbors:
                if nb.index in done:
                    continue
                else:
                    queue.append(nb)
        all_components.append((active, active_set))
        active, active_set = [], set()

    if len(all_components) == 1:
        connected = True
    else:
        connected = False
    while len(all_components) > 1:
        all_components.sort(key=lambda comp_set: len(comp_set[0]), reverse=True)
        comp, c_set = all_components.pop()
        rnd.shuffle(comp)

        # find cell in other component searching in direction as long as possible
        # if other cell from the same component is found
        #  set it as active and continue in the same direction
        found = False
        for cell in comp:
            cx, cy = positions[cell.index]
            for dx, dy in rnd.sample(((0, 1), (0, -1), (1, 0), (-1, 0)), k=4):
                ax, ay = cx, cy  # active_cell position
                fx, fy = cx, cy  # found_cell position
                active_cell = cell
                while True:
                    fx += dx
                    fy += dy
                    if not (0 <= fx < width and 0 <= fy < height):
                        break
                    found_cell = grid[fx][fy]
                    if found_cell is None:
                        continue
                    if found_cell.index in c_set:
                        active_cell = found_cell
                        ax, ay = fx, fy
                        continue
                    found = True
                    connected = True
                    break
                if found:
                    break
            if found:
                break
        if not found:
            if fail:
                return found
            else:
                continue

        # process mirror active cell
        ax2, ay2 = width - 1 - ax, height - 1 - ay
        active_mirror = grid[ax2][ay2]
        if active_mirror is active_cell:
            cells1 = (active_cell,) * 2
            comps1 = ((comp, c_set),)
        else:
            if found_cell is active_mirror:
                add_neighbors((active_cell,), (found_cell,))
                other_comp_index = find_component_index(found_cell.index)
                all_components[other_comp_index][0].extend(comp)
                all_components[other_comp_index][1].update(c_set)
                continue

            cells1 = (active_cell, active_mirror)

            if active_mirror.index in c_set:
                # active mirror is in the same component
                comps1 = ((comp, c_set),)
            else:
                other_comp_index = find_component_index(active_mirror.index)
                if found_cell.index in all_components[other_comp_index][1]:
                    # found cell in the same component as active_mirror
                    comps1 = ((comp, c_set),)
                else:
                    comps1 = (
                        (comp, c_set),
                        all_components.pop(other_comp_index),
                    )

        # process mirror found cell and connect components
        fx2, fy2 = width - 1 - fx, height - 1 - fy
        found_mirror = grid[fx2][fy2]

        if (
            found_cell is found_mirror
            or found_mirror.index in comps1[0][1]
            or (len(comps1) > 1 and found_mirror.index in comps1[1][1])
        ):
            # found cells are in the same component
            if found_cell is found_mirror and cells1[0] is cells1[1]:
                add_neighbors(cells1, (found_cell,))
            else:
                add_neighbors(cells1, (found_cell, found_mirror))
            other_comp_index = find_component_index(found_cell.index)
            connect_components(comps1, (other_comp_index,) * 2)
        else:
            add_neighbors(cells1, (found_cell, found_mirror))
            other_comp_index = find_component_index(found_cell.index)
            other_comp_index2 = find_component_index(found_mirror.index)
            if len(comps1) == 1:
                if other_comp_index != other_comp_index2:
                    comps1 += (all_components.pop(other_comp_index2),)
                    if other_comp_index2 < other_comp_index:
                        other_comp_index -= 1
                connect_components(comps1, (other_comp_index,) * 2)
            else:
                connect_components(
                    comps1, (other_comp_index, other_comp_index2)
                )
    return connected


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
    assert 0.1 <= density <= 1
    assert 0 <= hole_probability <= 1
    d_inc = int(1 / density)
    x = sqrt(num_cells * d_inc / 40)
    half_width = ceil(4 * x)
    width, height = half_width * 2 + 1, ceil(5 * x)

    for i in range(10):
        counts = half_counts_of_cells_in_columns(
            num_cells, d_inc, width, half_width, height, rnd
        )

        grid = get_grid_with_holes(
            width, height, hole_probability, rnd, counts, half_width
        )

        cells = [gc.Cell(i) for i in range(num_cells)]
        # set owner
        for c in cells[: counts[0]]:
            c.owner = 1
        for c in cells[-counts[0] :]:
            c.owner = 2

        positions = set_neighbors_update_grid_get_positions(
            num_cells, cells, grid, half_width
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

    return (
        cells,
        owners,
        starting_cell_indices,
        total_armies,
        neighbors,
        positions,
        (width, height),
    )
