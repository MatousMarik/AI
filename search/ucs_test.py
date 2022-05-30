#!/usr/bin/env python3
from ucs import ucs
from search_templates import Problem
from problems import Empty, Unsolvable, Graph, Line, Grid
from time import perf_counter


def run_test(prob: Problem):
    start = perf_counter()
    solution = ucs(prob)
    elapsed = (perf_counter() - start) * 1000

    if solution is None:
        if isinstance(prob, Unsolvable):
            print('"solved" in {:.3f} ms'.format(elapsed))
        else:
            print("found no solution in {:.3f} ms".format(elapsed))
        return

    if solution.report(prob):
        print("solved in {:.3f} ms".format(elapsed))


if __name__ == "__main__":
    problems = [Empty, Unsolvable, Graph, Line, Grid]

    for p in problems:
        print(f"Running test {p.__name__}")
        run_test(p())
        print()
