#!/usr/bin/env python3
from copy import deepcopy
from random import Random
from typing import List, Tuple, Optional

from minimax_templates import HeuristicGame, Strategy


class ConnectFour:
    """
    Represents ConnectFour game state.

    Also contain usefull methods for agent game play:
    - at
    - is_at
    - move
    - check_win
    - clone
    - actions
    - random_action

    Note: x, y coordinates start in top-left corner of the board
    """

    WIDTH = 7
    HEIGHT = 6
    DIRS = ((-1, -1), (-1, 0), (-1, 1), (0, 1))  # ((dir_x, dir_y))
    PATTERNS = ((0, 1, 0, 1, 0), (0, 0, 1, 1, 0), (0, 1, 1, 0, 0))

    def __init__(self, seed: int = 0):
        self.turn: int = 1
        self.winner: int = -1
        self.win: Tuple[int, int, int, int] = None  # (x, y, dx, dy)
        self.counter: int = 0
        self.random = Random(seed)
        self.board: bytearray = None
        self.init_moves: List[Tuple[int, int]] = None  # [(x, y),...]

        # init board so player1 won't need to win with perfect play
        while True:
            self.board = bytearray(self.WIDTH * self.HEIGHT)
            self.init_moves = []
            for m in self.random.choices(range(self.WIDTH), k=4):
                self.init_moves.append(self.move(m)[1])

            if not self._p1_win():
                break

        self._last_move: int = -1

    def at(self, x: int, y: int) -> int:
        """Return player occupying given position. (0 for free)."""
        if not 0 <= x < self.WIDTH or not 0 <= y < self.HEIGHT:
            raise ValueError("Invalid position ({}, {}).".format(x, y))
        return self.board[self.WIDTH * y + x]

    def is_at(self, x: int, y: int, player: int) -> bool:
        """Return whether given player is at given position."""
        return (
            0 <= x < self.WIDTH
            and 0 <= y < self.HEIGHT
            and self.board[self.WIDTH * y + x] == player
        )

    def _p1_win(self) -> bool:
        """Check player1 win with perfect play."""
        for x in range(self.WIDTH - 4):
            for pattern in self.PATTERNS:
                if all(
                    self.board[self.WIDTH * (self.HEIGHT - 1) + x + i]
                    == pattern[i]
                    for i in range(5)
                ):
                    return True
        return

    def _move_y(self, x: int) -> int:
        """Find y position for move = x-position only."""
        y = self.HEIGHT - 1
        while y >= 0 and self.board[self.WIDTH * y + x] > 0:
            y -= 1
        return y

    def valid(self, x, y) -> bool:
        """Check position on the board."""
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def move(self, x: int) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Execute given action - x-position move.

        Returns if move was completed and its (x, y) position in the board.
        """
        if x < 0 or x >= self.WIDTH:
            return False, None

        y = self._move_y(x)

        if y < 0:
            return False, None

        self.board[self.WIDTH * y + x] = self.turn
        self.counter += 1
        self._last_move = x
        self.check_win(x, y)
        self.turn = 3 - self.turn
        return True, (x, y)

    def check_win(
        self, x: int, y: int, set: bool = True, swap_turn: bool = False
    ) -> bool:
        """
        Return whether active player (or the other with 'swap_turn') win
        after placing token at given position and set winner and win if 'set'.
        """
        turn = 3 - self.turn if swap_turn else self.turn
        start = [-1, -1]
        for dir in self.DIRS:
            if self.winning_move(x, y, dir, start, turn):
                if set:
                    self.win = (start[0], start[1], *dir)
                    self.winner = self.turn
                return True

        if set and self.counter == self.WIDTH * self.HEIGHT:
            self.winner = 0
        return False

    def winning_move(
        self, x: int, y: int, dir: int, start: List[int], player: int
    ) -> bool:
        """
        Return whether player wins in given direction with token at given position.
        If so, set first position to start.
        """
        dx, dy = dir
        count = 0
        start_x, start_y = x, y

        while True:
            sx, sy = start_x - dx, start_y - dy
            if not self.is_at(sx, sy, player):
                break
            start_x, start_y = sx, sy
            count += 1

        end_x, end_y = x, y

        while True:
            ex, ey = end_x + dx, end_y + dy
            if not self.is_at(ex, ey, player):
                break
            end_x, end_y = ex, ey
            count += 1

        if count >= 3:
            start[0], start[1] = start_x, start_y
            return True
        else:
            return False

    def clone(self) -> "ConnectFour":
        """Return deepcopy of self state."""
        return deepcopy(self)

    def actions(self) -> List[int]:
        """Return possible actions in self state."""
        return [x for x in range(self.WIDTH) if self.at(x, 0) == 0]

    def random_action(self, random) -> int:
        """Return random action."""
        return random.choice(self.actions())


class ConnectFourGame(HeuristicGame):
    """Implementation of HeuristicGame providing IFace for ConnectFour."""

    outcomes = (
        HeuristicGame.DRAW,
        HeuristicGame.PLAYER_1_WIN,
        HeuristicGame.PLAYER_2_WIN,
    )

    def initial_state(self, seed: int) -> ConnectFour:
        return ConnectFour(seed)

    def clone(self, state: ConnectFour) -> ConnectFour:
        return state.clone()

    def player(self, state: ConnectFour) -> int:
        return state.turn

    def actions(self, state: ConnectFour) -> List[int]:
        return state.actions()

    def apply(self, state: ConnectFour, action: int) -> None:
        if not state.move(action)[0]:
            raise ValueError("illegal move")

    def is_done(self, state: ConnectFour) -> bool:
        return state.winner >= 0

    def outcome(self, state: ConnectFour) -> float:
        return ConnectFourGame.outcomes[state.winner]

    def evaluate(self, state: ConnectFour) -> float:
        return HeuristicStrategy.evaluate(state)


class BasicStrategy(Strategy):
    """
    Simple strategy for ConnectFour game.

    Try to play winning move (even for opponent) otherwise play random move.
    """

    def action(self, game: ConnectFour):
        possible = []
        block = -1
        for x in range(game.WIDTH):
            y = game._move_y(x)
            if y >= 0:
                if game.check_win(x, y, False):
                    return x

                if game.check_win(x, y, False, True):
                    block = x
                else:
                    possible.append(x)
        return block if block > -1 else self.random.choice(possible)


class HeuristicStrategy(Strategy):
    """
    Advanced strategy for ConnectFour game.
    """

    # values[n] is the value of having n discs within a span of 4 adjacent
    # positions, if the opponent has no discs in those positions.
    values = [0.0, 0.2, 1.0, 3.0, 100.0]

    @classmethod
    def _count(self, state: ConnectFour, p, x, y, dx, dy) -> bool:
        """Fill p"""
        if not state.valid(x, y) or not state.valid(x + 3 * dx, y + 3 * dy):
            return False

        p[0] = p[1] = p[2] = 0
        for i in range(4):
            p[state.board[x + i * dx + (y + i * dy) * state.WIDTH]] += 1
        return True

    @classmethod
    def _value(self, p) -> float:
        if p[1] > 0 and p[2] == 0:
            return self.values[p[1]]

        if p[2] > 0 and p[1] == 0:
            return -self.values[p[2]]
        return 0

    @classmethod
    def evaluate(self, state: ConnectFour) -> float:
        total = 0
        p = [0, 0, 0]
        for x in range(state.WIDTH):
            for y in range(state.HEIGHT):
                for dir in state.DIRS:
                    if self._count(state, p, x, y, *dir):
                        total += self._value(p)

    def action(self, state: ConnectFour) -> int:
        possible = []
        p = [0, 0, 0]
        best_val = -1e10
        block = -1

        for x in range(state.WIDTH):
            y = state._move_y(x)

            if y < 0:
                continue
            if state.check_win(x, y, False):
                return x
            if state.check_win(x, y, False, True):
                block = x
            if block != -1:
                continue

            # Calculate the incremental change in the heuristic score if we play at x.
            total = 0
            for dx, dy in state.DIRS:
                for i in range(4):
                    if self._count(state, p, x - i * dx, y - i * dy, dx, dy):
                        total -= self._value(p)
                        p[state.turn] += 1
                        total += self._value(p)

            if state.turn == 2:
                total = -total
            if total > best_val:
                best_val = total
                possible.clear()
            if total >= best_val:
                possible.append(x)

        return block if block >= 0 else self.random.choice(possible)
