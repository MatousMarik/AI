from csp_templates import Constraint, BooleanCSP
from typing import List, Optional


class Solver:
    """
    Class for solving BooleanCSP.

    Main methods:
    - forward_check
    - solve
    - infer_var
    """

    def __init__(self):
        # Your implementation goes here.
        pass

    def forward_check(self, csp: BooleanCSP) -> Optional[List[int]]:
        """
        Perform forward checking on any unchecked constraints in the given CSP.
        Return a list of variables (if any) whose values were inferred.
        If a contradiction is found, return None.
        """
        # Your implementation goes here.
        raise NotImplementedError

    def solve(self, csp: BooleanCSP) -> Optional[List[int]]:
        """
        Find a solution to the given CSP using backtracking.
        The solution will not include values for variables
        that do not belong to any constraints.
        Return a list of variables whose values were inferred.
        If no solution is found, return None.
        """
        # Your implementation goes here.
        raise NotImplementedError

    def infer_var(self, csp: BooleanCSP) -> int:
        """
        Infer a value for a single variable
        if possible using a proof by contradiction.
        If any variable is inferred, return it; otherwise return -1.
        """
        # Your implementation goes here.
        raise NotImplementedError
