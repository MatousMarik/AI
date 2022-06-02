#!/usr/bin/env python3
from game.action import *
from game.board import *
from game.artificial_agent import ArtificialAgent
from typing import List
from time import perf_counter


class Simple_Agent(ArtificialAgent):
    """Example Sokoban Agent implementation - tree DFS."""

    def __init__(self, optimal: bool = False, verbose: bool = False) -> None:
        """Really simple Tree-DFS agent."""
        super().__init__(optimal, verbose)  # recommended

        # you can add your instance variables here
        self.board: Board = None
        self.searched_nodes: int = 0

    def new_game(self) -> None:
        """Agent got into a new level."""
        super().new_game()

        # you can reset your instance variables here
        self.board = None

    def think(self, board: Board) -> List[EDirection]:
        self.board = board
        self.searched_nodes = 0

        start = perf_counter()
        result = []
        self.dfs(5, result)
        search_time = perf_counter() - start  # seconds

        if self.verbose < 0:
            print(f"Nodes visited: {self.searched_nodes}")
            print(
                f"Performance: {self.searched_nodes / search_time :.1f} nodes/sec"
            )

        return result if result else None

    def dfs(self, level: int, result: list) -> bool:
        if level <= 0:
            return False  # depth-limited

        self.searched_nodes += 1

        # possible actions
        actions: List[Action] = []
        for m in Move.get_actions():
            if m.is_possible(self.board):
                actions.append(m)
        for p in Push.get_actions():
            if p.is_possible(self.board):
                actions.append(p)

        # try actions
        for a in actions:
            # perform the action
            result.append(a.get_direction())
            a.perform(self.board)

            # check victory
            if self.board.is_victory():
                return True

            # continue search
            if self.dfs(level - 1, result):
                return True

            # no solution found from this state - reverse action
            result.pop()
            a.reverse(self.board)

        return False
