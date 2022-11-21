#!/usr/bin/env python3
from copy import deepcopy
from typing import List, Optional
from random import Random

from minimax_templates import HeuristicGame, Strategy


class TicTacToe:
    """Game state for TicTacToe."""

    MAP_VAL_TO_CHAR = {0: ".", 1: "O", 2: "X"}

    def __init__(self, board: bytearray = None):
        """Note: for given board does not check wether board is valid and does not change turns"""
        self.moves: int = 0
        self.turn: int = 1
        if board is None:
            self.board = bytearray(9)
        else:
            self.board = deepcopy(board)
            for b in self.board:
                if b != 0:
                    self.moves += 1
        self.winner_: int = -1

    def clone(self) -> "TicTacToe":
        """Return deep copy of self."""
        return deepcopy(self)

    def actions(self) -> List[int]:
        """Return list of valid actions."""
        return (
            [a for a, b in enumerate(self.board) if b == 0]
            if self.winner_ == -1
            else []
        )

    def random_action(self, random: Random) -> int:
        a = self.actions()
        return random.choice(a)

    def result(self, action: int) -> "TicTacToe":
        """Return resulting state after applying given action."""
        s = self.clone()
        s.move(action)
        return s

    def check_win(self) -> None:
        """Check wether any player is winner and if so set winner."""

        def win(x, y, dx, dy) -> bool:
            i = x * 3 + y
            di = dx * 3 + dy
            if (
                self.board[i] > 0
                and self.board[i]
                == self.board[i + di]
                == self.board[i + 2 * di]
            ):
                self.winner_ = self.board[i]
                self.win_x = x
                self.win_y = y
                self.win_dx = dx
                self.win_dy = dy
                return True
            return False

        for i in range(3):
            if win(i, 0, 0, 1) or win(0, i, 1, 0):
                return

        if win(0, 0, 1, 1) or win(0, 2, 1, -1):
            return

        if self.moves == 9:
            self.winner_ = 0

    def move(self, x_or_action: int, y: Optional[int] = None) -> bool:
        """
        Apply action. If action is invalid return False, otherwise return True.
        """
        if y is None:
            action = x_or_action
        else:
            action = 3 * x_or_action + y

        if action > 8 or action < 0 or self.board[action] != 0:
            return False

        self.board[action] = self.turn
        self.moves += 1
        self.check_win()
        self.turn = 3 - self.turn
        return True

    def winner(self) -> int:
        return self.winner_

    def as_char(self, i: int) -> str:
        return self.MAP_VAL_TO_CHAR[i]

    def player(self) -> int:
        return self.turn

    def __str__(self) -> str:
        l = [self.as_char(i) for i in self.board]
        for i in range(9, 2, -3):
            l.insert(i, "\n")
        return "".join(l)


class TicTacToeGame(HeuristicGame):
    """HeuristicGame intefface implementation for TicTacToe."""

    def initial_state(self, seed: int = None) -> TicTacToe:
        return TicTacToe()

    def clone(self, state: TicTacToe) -> TicTacToe:
        return state.clone()

    def player(self, state: TicTacToe) -> int:
        return state.player()

    def actions(self, state: TicTacToe) -> List[int]:
        return state.actions()

    def apply(self, state: TicTacToe, action: int) -> None:
        if not state.move(action):
            raise ValueError(action, "Illegal move.")

    def is_done(self, state: TicTacToe) -> bool:
        return state.winner() >= 0 or state.moves > 8

    MAP = {
        0: HeuristicGame.DRAW,
        1: HeuristicGame.PLAYER_1_WIN,
        2: HeuristicGame.PLAYER_2_WIN,
    }

    def outcome(self, state: TicTacToe) -> float:
        return self.MAP[state.winner()]

    def evaluate(self, state: TicTacToe) -> float:
        return self.DRAW


class BasicStrategy(Strategy):
    """
    A basic strategy for Tic-Tac-Toe.

    If any move will win, play it.  Otherwise, if any move will block an opponent's
    immediate win, play it.  Otherwise, play a random move.
    """

    def __init__(self, seed=None):
        super().__init__(seed)

    def action(self, state: TicTacToe) -> int:
        s = state.clone()
        for player in [s.turn, 3 - s.turn]:
            for a in range(9):
                if s.board[a] == 0:
                    s.board[a] = player
                    s.check_win()
                    if s.winner_ == player:
                        return a
                    s.board[a] = 0
        return state.random_action(self.random)
