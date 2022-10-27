#!/usr/bin/env python3
from os import remove
from game.board import Board, ETile
from os.path import dirname, exists
from os.path import join as path_join
import sys
from typing import List, Union

from dead_square_detector import detect

LEVEL_SET = "Aymeric_du_Peloux_1_Minicosmos"
LIMIT = 10

DIR = path_join(dirname(__file__), "game", "levels")
SOLUTION = None  # "dead_squares_expected.txt"

TMP_FILE = "tmp_dead.txt"


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


def print_detected(level_set):
    file = path_join(DIR, f"{level_set}.sok")
    if not exists(file):
        print("Can't find level file")
        return

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


def test(
    level_set=LEVEL_SET,
    expected=SOLUTION,
    tmp_file=TMP_FILE,
    remove_tmp_file=True,
) -> Union[bool, None]:
    """
    Test dead squares detection:

    If expected is None just print the detections and return None.

    If tmp_file is None print detection to stdout
    else print detections into tmp_file.

    If expected is not None compare it with tmp_file
    and return True if matching.

    Remove created tmp_file if remove_tmp_file is True.
    """
    if expected is not None and tmp_file is None:
        tmp_file = TMP_FILE
        remove_tmp_file = True

    if tmp_file is not None:
        out = open(tmp_file, "w+")
        stdout_save = sys.stdout
        sys.stdout = out

    print_detected(level_set)

    if tmp_file is not None:
        out.close()
        sys.stdout = stdout_save

    if expected is not None:
        solution = path_join(dirname(__file__), expected)
        with open(tmp_file, "r") as det, open(solution, "r") as exp:
            i = 1
            dl, el = det.readline(), exp.readline()
            while dl == el and dl != "":
                dl, el = det.readline(), exp.readline()
                i += 1
            if dl == el:
                result = True
                print("OK")
            else:
                result = False
                print(
                    f"Mismatch on line {i}:\nExpected:\n{el}\nDetected:\n{dl}"
                )
        if remove_tmp_file:
            remove(tmp_file)
        else:
            print(f"Detections file created: {tmp_file}.")
        return result

    else:
        return None


if __name__ == "__main__":
    test()
