#!/usr/bin/env python3
from game.board import Board, EDirection, ETile
from typing import List, Tuple
from abc import ABC, abstractmethod


class Action(ABC):
    """IFace for Sokoban action."""

    @abstractmethod
    def get_direction(self) -> EDirection:
        pass

    @abstractmethod
    def is_possible(self, board: Board) -> bool:
        pass

    @abstractmethod
    def perform(self, board: Board) -> None:
        pass

    @abstractmethod
    def reverse(self, board: Board) -> None:
        pass


class Move(Action):
    """
    Sokoban moves one tile in selected direction without pushing box.

    Note: You should not initialize new instances.
    """

    actions = None

    def __init__(self, dir: EDirection) -> None:
        self.dir: EDirection = dir

    def get_direction(self) -> EDirection:
        return self.dir

    @classmethod
    def or_push(cls, board: Board, dir: EDirection) -> Action:
        """
        Return Move(dir) if move is possible otherwise return Push(dir).
        Note that returned Push action does not have to be possible.
        """
        action: Action = Move.get_action(dir)
        if action.is_possible(board):
            return action
        else:
            return Push.get_action(dir)

    @classmethod
    def get_actions(cls) -> List["Move"]:
        """Return all possibilities of Move actions."""
        return cls.actions

    @classmethod
    def get_action(cls, dir: EDirection) -> "Move":
        """Return move into given direction."""
        return cls.actions[dir.index]

    def is_possible(self, board: Board) -> bool:
        # edge
        if not board.on_board(*board.player, self.dir):
            return False

        # tile is not free
        if not ETile.is_free(
            board.tile(
                board.player[0] + self.dir.dx, board.player[1] + self.dir.dy
            )
        ):
            return False
        return True

    def perform(self, board: Board) -> None:
        """Perform the move, no validation!"""
        board.move_player(self.dir)

    def perform_with_result(
        self, board: Board
    ) -> Tuple[Tuple[int, int, str], Tuple[int, int, str]]:
        """
        Perform the move, no validation!

        Return list of changed positions
        and new string representation of tile
        ((x, y, 't'), ...)
        """
        p = board.player
        board.move_player(self.dir)
        return (
            (*p, ETile.str_repr(board.tile(*p))),
            (*board.player, ETile.str_repr(board.tile(*board.player))),
        )

    def reverse(self, board: Board) -> None:
        """Reverse this move PREVIOUSLY done by perform, no validation."""
        board.move_player(self.dir.opposite())

    def reverse_with_result(
        self, board: Board
    ) -> Tuple[Tuple[int, int, str], Tuple[int, int, str]]:
        """
        Reverse this move PREVIOUSLY done by perform, no validation.

        Return list of changed positions
        and new string representation of tile
        ((x, y, 't'), ...)
        """
        p = board.player
        board.move_player(self.dir.opposite())
        return (
            (*p, ETile.str_repr(board.tile(*p))),
            (*board.player, ETile.str_repr(board.tile(*board.player))),
        )

    def __str__(self) -> str:
        return f"Move[{self.dir}]"


Move.actions = [Move(dir) for dir in EDirection]


class Push(Action):
    """
    Sokoban moves box in selected direction to that direction
    and then moves itself onto freed tile.

    Note: You should not initialize new instances.
    """

    actions = None

    def __init__(self, dir: EDirection):
        self.dir: EDirection = dir

    def get_direction(self) -> EDirection:
        return self.dir

    @classmethod
    def get_actions(cls) -> List["Push"]:
        """Return all possibilities of Push actions."""
        return cls.actions

    @classmethod
    def get_action(cls, dir: EDirection) -> "Move":
        """Return push into given direction."""
        return cls.actions[dir.index]

    def is_possible(self, board: Board) -> bool:
        px, py = board.player

        # edge
        if not board.on_board(px, py, self.dir):
            return False

        # no box
        if not ETile.is_box(board.ptile(self.dir)):
            return False

        # box on edge
        if not board.on_board(px + self.dir.dx, py + self.dir.dy, self.dir):
            return False

        # tile next to box is not free
        if not ETile.is_free(
            board.tile(
                px + self.dir.dx + self.dir.dx, py + self.dir.dy + self.dir.dy
            )
        ):
            return False
        return True

    def perform(self, board: Board) -> None:
        """Perform the PUSH, no validation."""
        board.move_box(self.dir)
        board.move_player(self.dir)

    def perform_with_result(
        self, board: Board
    ) -> Tuple[
        Tuple[int, int, str], Tuple[int, int, str], Tuple[int, int, str]
    ]:
        """
        Perform the PUSH, no validation.

        Return list of changed positions
        and new string representation of tile
        ((x, y, 't'), ...)
        """
        p = board.player
        board.move_box(self.dir)
        board.move_player(self.dir)
        nx = board.player[0] + self.dir.dx
        ny = board.player[1] + self.dir.dy
        return (
            (*p, ETile.str_repr(board.tile(*p))),
            (*board.player, ETile.str_repr(board.tile(*board.player))),
            (nx, ny, ETile.str_repr(board.tile(nx, ny))),
        )

    def reverse(self, board: Board) -> None:
        """Reverse this action PREVIOUSLY done by perform, no validation."""
        board.move_player(self.dir.opposite())
        board.move_box(self.dir, rev=True)

    def reverse_with_result(
        self, board: Board
    ) -> Tuple[
        Tuple[int, int, str], Tuple[int, int, str], Tuple[int, int, str]
    ]:
        """
        Reverse this action PREVIOUSLY done by perform, no validation.

        Return list of changed positions
        and new string representation of tile
        ((x, y, 't'), ...)
        """
        p = board.player
        nx = p[0] + self.dir.dx
        ny = p[1] + self.dir.dy

        board.move_player(self.dir.opposite())
        board.move_box(self.dir, rev=True)

        return (
            (*p, ETile.str_repr(board.tile(*p))),
            (*board.player, ETile.str_repr(board.tile(*board.player))),
            (nx, ny, ETile.str_repr(board.tile(nx, ny))),
        )

    def __str__(self) -> str:
        return f"Push[{self.dir}]"


Push.actions = [Push(dir) for dir in EDirection]
