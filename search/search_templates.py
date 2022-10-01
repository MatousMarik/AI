#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import Union


class Problem(ABC):
    """Interface for search problem."""

    @abstractmethod
    def initial_state(self) -> object:
        """
        Return the initial state of the problem.

        :rtype: State
        """
        pass

    @abstractmethod
    def actions(self, state) -> list:
        """
        Return list of all available actions in a given state.

        :rtype: list of Actions
        """
        pass

    @abstractmethod
    def result(self, state, action) -> object:
        """
        Return state resulting from the application of a given action in a given state.
        Note: state should stay unchanged.

        :rtype: State
        """
        pass

    @abstractmethod
    def is_goal(self, state) -> bool:
        """
        Return whether a given state is goal state.
        """
        pass

    @abstractmethod
    def cost(self, state, action) -> float:
        """
        Return cost of the application of a given action in a given state.
        """
        pass


class HeuristicProblem(Problem):
    """Interface for heuristic problem."""

    @abstractmethod
    def estimate(self, state) -> float:
        """
        Return estimate of the cost of the cheapest path to the goal.
        """
        pass


class Optimal(ABC):
    @abstractmethod
    def optimal_cost(self) -> float:
        """Return cost of the optimal solution."""
        pass


class Solution:
    """
    Stores sequence of actions leading from some problem state
    to stored goal_state
    for stored path_cost
    """

    def __init__(
        self, actions: list, goal_state: object, path_cost: float
    ) -> None:
        self.actions = actions
        self.goal_state = goal_state
        self.path_cost = path_cost

    def is_valid(self, prob: Problem) -> bool:
        """
        Return whether sequence of actions leads to goal_state
        and whether the path_cost is correct.
        """
        state = prob.initial_state()
        cost = 0

        for action in self.actions:
            cost += prob.cost(state, action)
            state = prob.result(state, action)

        return (
            state == self.goal_state
            and prob.is_goal(state)
            and cost == self.path_cost
        )

    def is_optimal(self, prob: Problem) -> Union[None, bool]:
        """Return whether solution is optimal (None for unknown)."""
        if isinstance(prob, Optimal):
            if prob.optimal_cost() == self.path_cost:
                return True
            else:
                return False
        return None

    def report(self, prob: Problem) -> bool:
        """Report validity, cost and optimal cost if possible and return validity."""
        if not self.is_valid(prob):
            print("solution is invalid!")
            return False

        print("solution is valid")
        print(f"total cost is {self.path_cost}")
        op = self.is_optimal(prob)
        if op:
            print("solution is optimal")
        elif op is None:
            print("there is no optimal cost set for this problem")
        else:
            print("optimal cost is {}".format(prob.optimal_cost()))
        return True
