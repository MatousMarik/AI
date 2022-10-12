#!/usr/bin/env python3
from ucs import ucs
from search_templates import Problem
from problems import Empty, Unsolvable, Graph, Line, Grid
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
    solution = ucs(prob)
    elapsed = (perf_counter() - start) * 1000

    if solution is None:
        if isinstance(prob, Unsolvable):
            if verbose:
                print('"solved" in {:.3f} ms'.format(elapsed))
        else:
            if verbose:
                print("found no solution in {:.3f} ms".format(elapsed))
        return True, elapsed, True

    valid = None
    if verbose and (valid := solution.report(prob)):
        print("solved in {:.3f} ms".format(elapsed))

    return (
        valid if valid is not None else solution.is_valid(),
        elapsed,
        solution.is_optimal(prob),
    )


if __name__ == "__main__":
    problems = [Empty, Unsolvable, Graph, Line, Grid]

    for p in problems:
        print(f"Running test {p.__name__}")
        run_test(p())
        print()
