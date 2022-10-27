#!/usr/bin/env python3
from search_templates import Problem
from astar import AStar
from problems import Unsolvable, Cube, OptNPuzzle, PuzzleState
from time import perf_counter
from typing import Tuple, Union


def run_test(
    prob: Problem, *, verbose: bool = True
) -> Tuple[bool, float, Union[None, bool]]:
    """
    Run test and return validity, time and optimality (None for unknown).

    Call with verbose=False to turn off prints.
    """
    start = perf_counter()
    solution = AStar(prob)
    elapsed = perf_counter() - start

    if solution is None:
        if isinstance(prob, Unsolvable):
            if verbose:
                print('"solved" in {:.4f} s'.format(elapsed))
        else:
            if verbose:
                print("found no solution in {:.4f} s".format(elapsed))
        return True, elapsed, True

    valid = None
    if verbose and (valid := solution.report(prob)):
        print("solved in {:.4f} s".format(elapsed))

    return (
        valid if valid is not None else solution.is_valid(),
        elapsed,
        solution.is_optimal(prob),
    )


if __name__ == "__main__":
    print("Testing Cube")
    run_test(Cube())
    print()

    print("Testing NPuzzle")
    puzzles = [
        # shortest solution = 46 steps
        # A* with the taxicab heuristic will explore about 600,000 states
        ([2, 11, 14, 3, 8, 6, 7, 13, 0, 5, 4, 15, 1, 9, 10, 12], 46),
        # shortest solution = 44 steps
        # A* with the taxicab heuristic will explore about 1,400,000 states
        ([12, 9, 6, 2, 10, 5, 4, 3, 1, 8, 11, 14, 7, 0, 13, 15], 44),
    ]
    for puzzle, optimal_cost in puzzles:
        state = PuzzleState(puzzle)
        print(state)
        run_test(OptNPuzzle(state, optimal_cost))
        print()
