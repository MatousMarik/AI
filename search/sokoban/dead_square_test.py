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
SOLUTION = "dead_squares_expected.txt" # None

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
            dl, el = det.readline(), exp.readline()
            det_lns = []
            exp_lns = []
            store = False
            result = True
            while dl != "":
                if (dl.startswith("=")):    # name of level
                    print(dl, end="")
                    det_lns = []
                    exp_lns = []
                    store = False
                if (store):     # storing solution
                    det_lns.append(dl)
                    exp_lns.append(el)
                if (dl.startswith("dead squares:")):    # start storing solution
                    store = True
                if (store and dl == "\n"):  # end of solution, check it
                    store = False
                    check = True
                    for i in range(len(det_lns)):
                        if (det_lns[i] != exp_lns[i]):
                            check = False
                            result = False
                    if (not check):
                        print("Wrong solution!")
                        print("Expected:" + "\t" + "Detected:")
                        for i in range(len(det_lns)):
                            print(exp_lns[i].rstrip() + "\t",end="")
                            print(det_lns[i],end="")
                    else:
                        print("OK")
                dl, el = det.readline(), exp.readline()
        if remove_tmp_file:
            remove(tmp_file)
        else:
            print(f"Detections file created: {tmp_file}.")
        return result

    else:
        return None


if __name__ == "__main__":
    test()
