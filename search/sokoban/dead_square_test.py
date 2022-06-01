#!/usr/bin/env python3
from game.board import Board, ETile
from os.path import dirname, exists
from os.path import join as path_join
from typing import List

from dead_square_detector import detect

LEVEL_SET = "Aymeric_du_Peloux_1_Minicosmos"
LIMIT = 10

DIR = path_join(dirname(__file__), "game", "levels")


def print_targets(board: Board):
    for y in range(board.height):
        for x in range(board.width):
            tile = board.tile(x, y)
            if ETile.is_wall(tile):
                print("#", end="")
            elif ETile.is_target(tile):
                print(".", end="")
            else:
                print(" ", end="")
        print()
    print()


def print_dead(dead: List[List[bool]], board: Board):
    print("dead squares:")
    for y in range(board.height):
        for x in range(board.width):
            print(
                "#"
                if ETile.is_wall(board.tile(x, y))
                else "X"
                if dead[x][y]
                else "_",
                end="",
            )
        print()
    print()


if __name__ == "__main__":
    file = path_join(DIR, f"{LEVEL_SET}.sok")
    if not exists(file):
        print("Can't find level file")
        exit()

    skips = 0
    count = 0
    while count < LIMIT:
        board, _, skips = Board.from_file(file, None, skip=skips)

        if board is None:
            break

        count += 1

        print("== level {} ==\n".format(board.level_name))
        print_targets(board)

        dead = detect(board)
        print_dead(dead, board)
