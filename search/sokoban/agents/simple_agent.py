#!/usr/bin/env python3
from game.action import *
from game.board import *
from game.artificial_agent import ArtificialAgent
from typing import List
from time import perf_counter


class Simple_Agent(ArtificialAgent):
    """Example Sokoban Agent implementation - tree DFS."""

    DEPTH: int = 15

    @staticmethod
    def think(board: Board, optimal: bool, verbose: bool) -> List[EDirection]:
        searched_nodes = 0

        def dfs(level: int, result: list) -> bool:
            nonlocal searched_nodes, board
            if level <= 0:
                return False  # depth-limited

            searched_nodes += 1

            # possible actions
            actions: List[Action] = []
            for m in Move.get_actions():
                if m.is_possible(board):
                    actions.append(m)
            for p in Push.get_actions():
                if p.is_possible(board):
                    actions.append(p)

            # try actions
            for a in actions:
                # perform the action
                result.append(a.get_direction())
                a.perform(board)

                # check victory
                if board.is_victory():
                    return True

                # continue search
                if dfs(level - 1, result):
                    return True

                # no solution found from this state - reverse action
                result.pop()
                a.reverse(board)

            return False

        start = perf_counter()
        result = []
        dfs(Simple_Agent.DEPTH, result)
        search_time = perf_counter() - start  # seconds

        if verbose:
            print(f"Nodes visited: {searched_nodes}")
            print(f"Performance: {searched_nodes / search_time :.1f} nodes/sec")

        return result
