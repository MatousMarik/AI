#!/usr/bin/env python3
from search_templates import Problem, HeuristicProblem, Optimal
from collections import namedtuple
import random
from enum import IntEnum, Enum
from typing import List, Union


class Empty(Problem, Optimal):
    """
    Model search problem testing goal checking.
    """

    def initial_state(self):
        return 0

    def actions(self, state) -> list:
        return []

    def result(self, state, action):
        raise AssertionError("should not be called")

    def is_goal(self, state) -> bool:
        return state == 0

    def cost(self, state, action) -> float:
        raise AssertionError("should not be called")

    @classmethod
    def optimal_cost(cls) -> int:
        return 0


class Unsolvable(Problem):
    """
    Model search problem testing goal checking.
    """

    def initial_state(self):
        return 0

    def actions(self, state) -> list:
        return [1, 2, 3]

    def result(self, state, action):
        return min(state + action, 10)

    def is_goal(self, state) -> bool:
        return False

    def cost(self, state, action) -> float:
        return 1


class Graph(Optimal, Problem):
    """Model search problem testing graph."""

    Edge = namedtuple("Edge", ["dest", "weight"])

    def __init__(self):
        self.adj = [[] for _ in range(5)]

        def edge(u, v, weight):
            self.adj[v].append(Graph.Edge(u, weight))
            self.adj[u].append(Graph.Edge(v, weight))

        edge(0, 1, 5)
        edge(0, 2, 3)
        edge(1, 2, 1)
        edge(1, 3, 1)
        edge(1, 4, 3)
        edge(2, 3, 4)
        edge(3, 4, 1)

    def initial_state(self):
        return 0

    def actions(self, state) -> List[Edge]:
        return self.adj[state]

    def result(self, state, action: Edge):
        return action.dest

    def is_goal(self, state) -> bool:
        return state == 4

    def cost(self, state, action: Edge) -> int:
        return action.weight

    @classmethod
    def optimal_cost(cls) -> int:
        return 6


class Cube(Optimal, HeuristicProblem):
    """
    A simple model search problem involving movement in a cube.

    The start position is (1000, 1000, 1000).  The goal is to get to (0, 0, 0).  At each step
    the following moves are possible:

    - decrease X by 1 (cost: 1000)
    - decrease Y by 1 (cost: X)
    - decrease Z by 1 (cost: max(X, Y))

    The optimal strategy from any point is to first decrease X to 0, then decrease Y, then decrease Z.
    So the optimal cost from the start position of (1000, 1000, 1000) is 1,000,000.

    Uninformed uniform-cost search will be very expensive since it will explore
    millions of positions before finding the goal. With the right heuristic,
    A* will find the goal immediately, expanding exactly 3000 nodes.
    """

    CPos = namedtuple("CPos", "x y z")

    def initial_state(self) -> CPos:
        return Cube.CPos(1000, 1000, 1000)

    def actions(self, state: CPos) -> List[int]:
        return [a for a, c in enumerate(state, 1) if c > 0]

    def result(self, state: CPos, action: int) -> CPos:
        if action == 1:
            return Cube.CPos(state.x - 1, state.y, state.z)
        elif action == 2:
            return Cube.CPos(state.x, state.y - 1, state.z)
        elif action == 3:
            return Cube.CPos(state.x, state.y, state.z - 1)
        else:
            raise ValueError("unknown action")

    def is_goal(self, state: CPos) -> bool:
        return state.x == state.y == state.z == 0

    def cost(self, state: CPos, action: int) -> int:
        if action == 1:
            return 1000
        elif action == 2:
            return state.x
        elif action == 3:
            return max(state.x, state.y)

    def estimate(self, state: CPos) -> int:
        """
        The heuristic (1000 * state.x) is optimal and will lead to the goal immediately.

        A non-optimal heuristic such as (980 * state.x) will also lead to the goal pretty quickly.
        Performance will worsen as you decrease the constant.

        A heuristic of 0 degenerates to uniform-cost search, which will be hopelessly slow.
        """
        return 1000 * state.x

    @classmethod
    def optimal_cost(cls) -> int:
        return 1_000_000


class Grid(Optimal, Problem):
    """
    A simple puzzle involving movement on a grid.

    You start at (0, 0).  In each move you may move either
    - left 1 (cost = 1)
    - right 1 (cost = 1)
    - up 1 (cost = 1)
    - down 1 (cost = 1)
    - right 1, up 2 (cost = 2)
    - right 2, up 2 (cost = 5)

    The goal is to get to (80, 80) with minimal total cost.
    The cheapest solution has cost = 120.
    """

    GPos = namedtuple("GPos", "x y")
    GPos.plus = lambda self, v: Grid.GPos(self.x + v[0], self.y + v[1])

    class Move(Enum):
        L1 = ((-1, 0), 1)
        R1 = ((1, 0), 1)
        U1 = ((0, -1), 1)
        D1 = ((0, 1), 1)
        R1U2 = ((1, 2), 2)
        R2U2 = ((2, 2), 5)

        def __init__(self, v, c) -> None:
            self.vector = v
            self.cost = c

    def initial_state(self) -> GPos:
        return Grid.GPos(0, 0)

    def actions(self, state: GPos) -> List[Move]:
        return list(Grid.Move)

    def result(self, state: GPos, action: Move) -> GPos:
        return state.plus(action.vector)

    def is_goal(self, state: GPos) -> bool:
        return state.x == 80 == state.y

    def cost(self, state: GPos, action: Move) -> int:
        return action.cost

    @classmethod
    def optimal_cost(cls) -> int:
        return 120


class Line(Optimal, Problem):
    """
    A simple model search problem.
    """

    _cost = [None, 8, 3, 5]

    def initial_state(self) -> int:
        return 0

    def actions(self, state: int) -> List[int]:
        return [1, 2, 3]

    def result(self, state: int, action: int) -> int:
        return state + action

    def is_goal(self, state: int) -> bool:
        return state == 101

    def cost(self, state: int, action: int) -> int:
        return Line._cost[action]

    @classmethod
    def optimal_cost(cls) -> int:
        return 152


def isqrt(n: int) -> int:
    """Return integer square root."""
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


class PuzzleState:
    """State of NPuzzle problem."""

    def __init__(
        self, squares: List[int], size: int = None, empty: int = None
    ) -> None:
        self.size: int = isqrt(len(squares)) if size is None else size
        self.squares: List[int] = squares
        # index of empty square
        self.empty: int = (
            PuzzleState.find_empty(squares) if empty is None else empty
        )

    @staticmethod
    def find_empty(a: List[int]) -> int:
        for i, t in enumerate(a):
            if t == 0:
                return i
        raise ValueError("no empty square")

    @staticmethod
    def reversed(size: int) -> "PuzzleState":
        """Construct a puzzle where all the tiles are in reverse order."""
        return PuzzleState(list(range(size**2 - 1, -1, -1)))

    @staticmethod
    def random(size: int, num: int) -> "PuzzleState":
        """Construct a puzzle by making a number of random moves from the goal state."""
        state = PuzzleState(list(range(size**2)))
        for _ in range(num):
            l = state.possible_directions()
            state.slide(random.choice(l))
        return state

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, PuzzleState) and self.squares == __o.squares

    def possible_directions(self) -> List[int]:
        """Return valid directions to slide a tile."""
        dirs = []
        r = self.empty // self.size
        c = self.empty % self.size
        if r > 0:
            dirs.append(NPuzzle.Dir.Down)
        if r < self.size - 1:
            dirs.append(NPuzzle.Dir.Up)
        if c > 0:
            dirs.append(NPuzzle.Dir.Right)
        if c < self.size - 1:
            dirs.append(NPuzzle.Dir.Left)

        return dirs

    def slide(self, dir: int) -> "PuzzleState":
        """
        Apply slide in direction to a copy of the state
        and return resulting state.
        """
        if dir == 0:
            d = -1
        elif dir == 1:
            d = 1
        elif dir == 2:
            d = -self.size
        elif dir == 3:
            d = self.size
        else:
            raise ValueError("invalid direction")

        a = self.squares.copy()
        a[self.empty] = a[self.empty - d]
        a[self.empty - d] = 0
        return PuzzleState(a, self.size, self.empty - d)

    def is_goal(self) -> bool:
        for i, v in enumerate(self.squares):
            if i != v:
                return False
        return True

    def __hash__(self) -> int:
        return tuple(self.squares).__hash__()

    def __str__(self) -> str:
        return "\n".join(
            [
                " ".join(map(str, self.squares[i : i + self.size]))
                for i in range(0, self.size**2, self.size)
            ]
        )


class NPuzzle(HeuristicProblem):
    """
    The classic sliding block puzzle, i.e. the 8-puzzle or 15-puzzle.

    Construct the 8-puzzle like this:

    new NPuzzle(3);

    The starting position has the tiles in reversed order:

    8 7 6
    5 4 3
    2 1 _

    The goal position is

    _ 1 2
    2 3 4
    5 6 7

    The minimal solution has 28 steps.

    The heuristic function below is the sum of the Manhattan distances of tiles
    from their goal positions.  With this heuristic, A* should find the solution
    while expanding only a few hundred nodes.

    The corresponding 15-puzzle is

    new NPuzzle(4);

    This is much harder, and requires pattern databases to solve effectively.
    """

    Dir = type("Dir", (), dict(Left=0, Right=1, Up=2, Down=3))

    def __init__(self, init: Union[PuzzleState, int]) -> None:
        if isinstance(init, PuzzleState):
            self.initial = init
        elif isinstance(init, int):
            self.initial = PuzzleState.reversed(init)
        else:
            raise ValueError("invalid initial parameter")
        self.dists = NPuzzle.get_dists(self.initial.size)

    @staticmethod
    def get_dists(size: int) -> List[List[int]]:
        dists = []
        for i in range(size**2):
            di = []
            for j in range(size**2):
                # taxicab distance
                di.append(abs(i // size - j // size) + abs(i % size - j % size))
            dists.append(di)
        return dists

    def initial_state(self) -> PuzzleState:
        return self.initial

    def actions(self, state: PuzzleState) -> List[int]:
        return state.possible_directions()

    def result(self, state: PuzzleState, action: int) -> PuzzleState:
        return state.slide(action)

    def is_goal(self, state: PuzzleState) -> bool:
        return state.is_goal()

    def cost(self, state: PuzzleState, action: int) -> int:
        return 1

    def estimate(self, state: PuzzleState) -> int:
        """Compute the sum of the taxicab distances of tiles from their goal positions."""
        sum = 0
        for i, s in enumerate(state.squares):
            if s > 0:
                sum += self.dists[s][i]
        return sum


class OptNPuzzle(NPuzzle, Optimal):
    """NPuzzle with optimal cost."""

    def __init__(self, init: Union[PuzzleState, int], opt_cost: int) -> None:
        NPuzzle.__init__(self, init)
        self._opt_cost = opt_cost

    def optimal_cost(self) -> int:
        return self._opt_cost
