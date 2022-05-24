#!/usr/bin/env python3
from search_templates import HeuristicProblem

from astar import AStar
from problems import Cube, OptNPuzzle, PuzzleState
from time import perf_counter


def run_test(prob: HeuristicProblem):
    start = perf_counter()
    solution = AStar(prob)
    elapsed = (perf_counter() - start) * 1000
    if solution.report(prob):
        print("solved in {:.0f} ms".format(elapsed))


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
