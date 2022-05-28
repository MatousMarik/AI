#!/usr/bin/env python3
from math import floor
from csp_templates import Constraint, BooleanCSP
from typing import Tuple, Optional, Dict
import random

from solver import Solver

# Some small problems that are solvable by forward checking.
easy = [
    "1 var: 1 of {0}",
    "1 var: 0 of {0}",
    "3 vars: 1 of {0}, 1 of {1}, 0 of {2}",
    "4 vars: 1 of {0 1}, 1 of {1 2}, 1 of {2 3}, 0 of {3}",
    "4 vars: 2 of {0 1 2 3}, 0 of {0 3}",
    "5 vars: 2 of {0 1 2 3 4}, 2 of {1 4}",
    "8 vars: 1 of {0 1 3 4}, 2 of {0 1 2 4 5 6 7}, 2 of {1 5}",
    "8 vars: 3 of {0 2 3 4 5 7}, 2 of {1 3 6 7}, 3 of {3 4 7}",
]

# These problems can't be solved by forward checking, but they are all satisfiable,
# so a backtracking search should find a solution for all of them.  Also, some
# inferences are possible in most of them.
harder = [
    "4 vars: 1 of {0 1}, 1 of {1 2}, 1 of {2 3}",
    "4 vars: 1 of {0 1}, 1 of {1 2}, 1 of {2 3}, 2 of {0 2 3} / 0=T, 1=F, 2=T, 3=F",
    # a situation from a 3 x 3 Minesweeper board
    "9 vars: 0 of {2 5 6}, 1 of {1 4 5}, 1 of {1 2 4 7 8}, 1 of {3 4 7} / 7=F, 8=F",
    # a situation from a 4 x 4 Minesweeper board
    "16 vars: 0 of {0 1 2 3 4 5 6 7}, 1 of {0 1 5 8 9}, 1 of {0 1 2 4 6 8 9 10}, "
    + "1 of {1 2 3 5 7 9 10 11}, 1 of {2 3 6 10 11} / 8=T, 9=F, 10=F, 11=T",
    # a situation from a 4 x 4 Minesweeper board
    "16 vars: 0 of {4 5 8 9 12 13}, 1 of {0 1 5 8 9}, 2 of {0 1 2 4 6 8 9 10}, "
    + "2 of {4 5 6 8 10 12 13 14}, 2 of {8 9 10 12 14} / 2=F, 6=F, 10=T, 14=T",
    # a situation from a 5 x 5 Minesweeper board
    "25 vars: 0 of {10 11 12 13 14 15 16 18 19 20 21 23 24}, "
    + "1 of {5 6 11 15 16}, 2 of {5 6 7 10 12 15 16 17}, "
    + "1 of {10 11 12 15 17 20 21 22}, 1 of {15 16 17 20 22}, "
    + "3 of {6 7 8 11 13 16 17 18}, "
    + "2 of {7 8 9 12 14 17 18 19}, 1 of {8 9 13 18 19}, "
    + "1 of {12 13 14 17 19 22 23 24}, 1 of {17 18 19 22 24} "
    + "/ 5=F, 6=T, 8=T, 9=F",
]

# More problems where some inferences are possible.
extra = [
    "8 vars: 1 of {0 1}, 2 of {0 1 2}, 1 of {1 2 3}, 3 of {2 3 4 5 6}, "
    + "2 of {5 6 7}, 1 of {6 7} / 0=T, 1=F, 2=T, 3=F, 5=T",
    "8 vars: 1 of {0 1}, 1 of {0 1 2}, 1 of {1 2 3}, 1 of {2 3 4 5 6}, "
    + "2 of {5 6 7}, 1 of {6 7} / 0=F, 1=T, 2=F, 3=F, 4=F, 5=T, 6=F, 7=T",
    "8 vars: 1 of {0 1}, 2 of {0 1 2}, 2 of {1 2 3 4 5}, 1 of {4 5 6}, "
    + "1 of {5 6 7} / 2=T",
    "7 vars: 1 of {0 1}, 1 of {0 1 2}, 1 of {1 2 3}, 1 of {2 3 4 5 6}, "
    + "1 of {5 6} / 0=F, 1=T, 2=F, 3=F, 4=F",
]


def str_values(a: list) -> str:
    return ", ".join(
        [
            "{0}={1}".format(var, "X" if val is None else "T" if val else "F")
            for var, val in enumerate(a)
        ]
    )


def random_forward_prob(size: int) -> BooleanCSP:
    """Generate a random CSP that can be solved by forward checking."""
    var_map = random.sample(range(size), k=size)

    vals = []
    csp = BooleanCSP(size)
    n = 0
    while n < size:
        prev = min(n, random.randrange(1, 5))
        new_vars = min(size - n, random.randrange(1, 5))

        sum_ = 0
        c_vars = []
        # select variables with value for constraint
        for i in random.sample(range(prev), k=prev):
            c_vars.append(var_map[i])
            sum_ += vals[i]

        # decide value for new variables and sets it
        val = 1 if sum_ == 0 else 0 if sum_ == prev else random.randrange(2)
        for i in range(n, n + new_vars):
            c_vars.append(var_map[i])
            vals.append(val)
            sum_ += val

        c_vars.sort()
        csp.add_constraint(Constraint(sum_, c_vars))
        n += new_vars
    return csp


def random_satisfiable(size: int) -> Tuple[BooleanCSP, str]:
    """
    Generate a random CSP that is satisfiable.
    Returns csp and solution string.
    """
    vals = random.choices([True, False], k=size)
    csp = BooleanCSP(size)
    for _ in range(floor(2 / 3 * size)):
        count = min(random.randrange(2, 6), size)
        vars = random.sample(range(size), k=count)
        sum_ = sum([vals[v] for v in vars])
        csp.add_constraint(Constraint(sum_, vars))
    return csp, "actual values:\n" + str_values(vals)


def parse(s: str, inferences: Optional[Dict] = None) -> BooleanCSP:
    """
    Parse csp problem from string to BooleanCSP.
    If inferences are provided and available it also fills inferences
    with as var -> val mapping.
    """
    top = s.split("/")
    parts = top[0].split(":")
    num_vars = int(parts[0].split(" ", maxsplit=1)[0])

    csp = BooleanCSP(num_vars)

    for c in parts[1].split(","):
        c = c.strip().split(" ", maxsplit=1)
        count = int(c[0])
        c = c[1].split("{")[1].split("}")[0].split(" ")
        vars = list(map(int, c))
        csp.add_constraint(Constraint(count, vars))

    if len(top) > 1 and inferences is not None:
        for a in top[1].split(","):
            a = a.strip().split("=")
            inferences[int(a[0])] = a[1] == "T"
    return csp


def check_solved(csp: BooleanCSP) -> Tuple[bool, str]:
    """Returns solved and error string."""
    for i, v in enumerate(csp.value):
        if v is None and csp.var_constraints[i]:
            return False, f"no value for {i}"

    for c in csp.constraints:
        count = 0
        for v in c.vars:
            if csp.value[v]:
                count += 1

        if count != c.count:
            return False, f"constraint {str(c)} not satisfied"
    return True, None


def test_forward(csp: BooleanCSP, solver: Solver) -> Tuple[bool, str]:
    """Return solved and error string."""
    found = solver.forward_check(csp)
    if found is None:
        return False, "failed to find a solution"
    if len(found) != csp.num_vars:
        return (
            False,
            "failed to solve all variables\nfound solution:\n"
            + str_values(csp.value),
        )

    fine, error = check_solved(csp)
    if fine:
        return True, None
    else:
        return False, error + "\nfound solution:\n" + str_values(csp.value)


def test_forward_easy(solver: Solver) -> bool:
    print("\ntesting forward checking")
    for pi, p in enumerate(easy, 1):
        solved, error = test_forward(parse(p, None), solver)
        if solved:
            print(f"problem {pi}: solved")
        else:
            print(p)
            print(error)
            return False
    return True


def test_forward_random(solver: Solver) -> bool:
    print("\ntesting forward checking on random problems")
    for size in range(10, 101, 10):
        csp = random_forward_prob(size)
        solved, error = test_forward(csp, solver)
        if solved:
            print(f"{size} vars: solved")
        else:
            print(csp)
            print(error)
            return False
    return True


def test_solve(csp: BooleanCSP, solver: Solver) -> Tuple[bool, str]:
    """Return solved and error string."""
    found = solver.solve(csp)
    if found is None:
        return False, "failed to find a solution"
    fine, error = check_solved(csp)
    if fine:
        return True, None
    else:
        return False, error + "\nfound solution:\n" + str_values(csp.value)


def test_solve_fixed(solver: Solver) -> bool:
    print("\ntesting solver")
    pi = 0
    for tests in [easy, harder]:
        for p in tests:
            pi += 1
            solved, error = test_solve(parse(p, None), solver)
            if solved:
                print(f"problem {pi}: solved")
            else:
                print(p)
                print(error)
                return False
    return True


def test_solve_random(solver: Solver) -> bool:
    print("\ntesting solver on random problems")
    for size in range(100, 1001, 100):
        csp, actual = random_satisfiable(size)
        solved, error = test_solve(csp, solver)
        if solved:
            print(f"{size} vars: solved")
        else:
            print(csp)
            print(error)
            print(actual)
            return False
    return True


def test_infer(problems, solver: Solver) -> bool:
    for pi, p in enumerate(problems, 1):
        expected = {}
        csp = parse(p, expected)

        # Repeatedly call forwardCheck() and inferVar() to infer as much as possible.
        while True:
            if solver.forward_check(csp) is None:
                print(p)
                print("forward inference failed")
                return False
            if solver.infer_var(csp) == -1:
                break

        # check inferences correspond to expected
        error = None
        for var, val in enumerate(csp.value):
            b = None
            for c in csp.var_constraints[var]:
                if c.count == 0:
                    b = False
                    break

            if b is None:
                if var in expected:
                    b = expected[var]
                    break
            if b is None and val is not None:
                error = f"should not have inferred value for var {var}"
                break
            if b is not None and val is None:
                error = f"should have inferred value for var {var}"
                break
            if b != val:
                error = f"inferred wrong value for var {var}"
                break
        if error is None:
            print(f"problem {pi}: solved")
        else:
            print(p)
            print(error)
            print("found solution:")
            print(str_values(csp.value))
            return False
    return True


def test_infer_fixed(solver: Solver) -> bool:
    print("\ntesting inference")
    return test_infer(harder, solver)


def test_infer_extra(solver: Solver) -> bool:
    print("\ntesting inference (extra)")
    return test_infer(extra, solver)


tests = [
    test_forward_easy,
    test_forward_random,
    test_solve_fixed,
    test_solve_random,
    test_infer_fixed,
    test_infer_extra,
]

if __name__ == "__main__":
    solver = Solver()
    success = True
    for test in tests:
        if not test(solver):
            success = False
            break
    if success:
        print("all tests passed")
