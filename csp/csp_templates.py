#!/usr/bin/env python3
from collections import deque
from typing import Deque, Set, List, Optional


class Constraint:
    """
    A constraint that says that exactly a certain number (count) of a certain set
    of variables are True.
    """

    def __init__(self, count: int, vars: List[int]) -> None:
        self.count: int = count
        self.vars: List[int] = vars

    def __str__(self) -> str:
        return "{} of {{{}}}".format(self.count, " ".join(map(str, self.vars)))


class BooleanCSP:
    """
    Represent CSP with uniform variable domain
    {True, False, None-Unknown}

    and provide basic methods for adding constraints,
    and setting values of variables.
    """

    def __init__(self, num_vars: int):
        # variables are numbered 0 .. (num_vars -1)
        self.num_vars: int = num_vars
        # value of each variable (None | True | False), None for unknown
        self.value: List[Optional[bool]] = [None] * num_vars
        # all constraints
        self.constraints: Set[Constraint] = set()
        # constraints affecting variable
        self.var_constraints: List[Set[Constraint]] = [
            set() for _ in range(num_vars)
        ]
        # constraints not yet checked by forward checking
        self.unchecked: Deque[Constraint] = deque()

    def add_constraint(self, c: Constraint) -> None:
        """
        Add new constraint and all resulting var_constraints.

        Constraint should contain only known variables
        Constraint is added to unchecked.
        """
        self.constraints.add(c)
        for v in c.vars:
            self.var_constraints[v].add(c)
        self.unchecked.append(c)

    def set(self, var: int, val: bool) -> None:
        """
        Set variable value
        and set all corresponding var_constraints as unchecked.
        """
        self.value[var] = val
        self.unchecked.extend(self.var_constraints[var])

    def reset(self, vars: List[int] = None) -> None:
        """
        Set values of all, or all specified variables to None.

        Does not modify unchecked.
        """
        for v in vars if vars is not None else range(self.num_vars):
            self.value[v] = None

    def __str__(self) -> str:
        return "{} vars: {}".format(
            self.num_vars, ", ".join(map(str, self.constraints))
        )
