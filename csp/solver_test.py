#!/usr/bin/env python3
from math import floor
from csp_templates import Constraint, BooleanCSP

from solver import Solver
import random


class Assignment:
    def __init__(self, var: int, value: bool):
        self.var: int = var
        self.value: bool = value


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
    random.seed(0)
    var_map = list(range(size))
    random.shuffle(var_map)

    vals = []
    csp = BooleanCSP(size)
    n = 0
    while n < size:
        prev = min(n, random.randrange(1, 5))
        new_vars = min(size - n, random.randrange(1, 5))

        sum_ = 0
        cvars = []
        while len(cvars) < prev:
            i = random.randrange(prev)
            if var_map[i] not in cvars:
                cvars.append(var_map[i])
                sum_ += vals[i]

        val = 1 if sum_ == 0 else 0 if sum_ == prev else random.randrange(2)
        for i in range(new_vars):
            cvars.append(var_map[n + i])
            vals.append(val)
            sum_ += val

        cvars.sort()
        csp.add_constraint(Constraint(sum_, cvars))
        n += new_vars
    return csp


def random_satisfiable(size: int) -> BooleanCSP:
    """Generate a random CSP that is satisfiable."""
    random.seed(0)
    vals = random.choices([True, False], k=size)
    print("actual values:", str_values(vals))
    csp = BooleanCSP(size)
    for _ in range(floor(2 / 3 * size)):
        count = min(random.randrange(2, 6), size)
        vars = random.sample(range(size), k=count)
        sum_ = sum([vals[v] for v in vars])
        csp.add_constraint(Constraint(sum_, vars))

    print(csp)
    return csp


def parse(s: str, inferences: None) -> BooleanCSP:
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
            inferences.append(Assignment(int(a[0]), a[1] == "T"))

    return csp


def check_solved(csp: BooleanCSP) -> bool:
    for i, v in enumerate(csp.value):
        if v == None and csp.var_constraints[i]:
            print(f"no value for {i}")
            return False

    for c in csp.constraints:
        count = 0
        for v in c.vars:
            if csp.value[v]:
                count += 1

        if count != c.count:
            print("constraint not satisfied")
            return False

    return True


def test_forward(csp: BooleanCSP, solver: Solver) -> bool:
    found = solver.forward_check(csp)
    if found is None:
        print("failed to find a solution")
        return False
    print(str_values(csp.value))
    if len(found) != csp.num_vars:
        "failed to solve all variables"
        return False
    return check_solved(csp)


def test_forward_easy(solver: Solver) -> bool:
    print("\ntesting forward checking")
    for p in easy:
        print(p)
        if not test_forward(parse(p, None), solver):
            return False
    return True


def test_forward_random(solver: Solver) -> bool:
    print("\ntesting forward checking on random problems")
    for size in range(10, 101, 10):
        csp = random_forward_prob(size)
        print(csp)
        if not test_forward(csp, solver):
            return False
    return True


def test_solve(csp: BooleanCSP, solver: Solver) -> bool:
    found = solver.solve(csp)
    if found is None:
        print("failed to find a solution")
        return False
    print("found solution:", str_values(csp.value))
    return check_solved(csp)


def test_solve_fixed(solver: Solver) -> bool:
    print("\ntesting solver")
    for tests in [easy, harder]:
        for p in tests:
            print(p)
            if not test_solve(parse(p, None), solver):
                return False
    return True


def test_solve_random(solver: Solver) -> bool:
    print("\ntesting solver on random problems")
    for size in range(100, 1001, 100):
        csp = random_satisfiable(size)
        if not test_solve(csp, solver):
            return False
    return True


def test_infer(probs, solver: Solver) -> bool:
    for p in probs:
        print(p)
        expected = []
        csp = parse(p, expected)

        # Repeatedly call forwardCheck() and inferVar() to infer as much as possible.
        while True:
            if solver.forward_check(csp) is None:
                print("forward inference failed")
                return False
            if solver.infer_var(csp) == -1:
                break

        print(str_values(csp.value))
        for var, val in enumerate(csp.value):
            b = None
            for c in csp.var_constraints[var]:
                if c.count == 0:
                    b = False
                    break

            if b is None:
                for a in expected:
                    if a.var == var:
                        b = a.value
                        break
            if b is None and val is not None:
                print(f"should not have inferrred value for var {var}")
                return False
            if b is not None and val is None:
                print(f"should have inferred value for var {var}")
                return False
            if b != val:
                print(f"inferred wrong value for var {var}")
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
