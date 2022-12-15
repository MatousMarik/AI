#!/usr/bin/env python3
from game.minesweeper import *
from game.artificial_agent import ArtificialAgent
from argparse import ArgumentParser
from random import sample as random_sample
from typing import List, Optional
import sys

from importlib.util import spec_from_file_location, module_from_spec
from os.path import join as path_join, dirname

AGENTS_DIR = path_join(dirname(__file__), "agents")


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "-a",
        "--agent",
        default=None,
        type=str,
        help="Agent to use, should be name of class in the file lowercase.py the"
        + " agent directory. (default player)",
    )
    parser.add_argument(
        "-s",
        "--sim",
        default=None,
        type=int,
        help="Simulate a series of games without visualization.",
    )

    g1 = parser.add_mutually_exclusive_group()
    g1.add_argument(
        "-d", "--density", type=float, help="Mines density. (default 0.2)"
    )
    g1.add_argument("-c", "--mine_count", type=int, help="Number of mines.")

    g2 = parser.add_mutually_exclusive_group()
    g2.add_argument(
        "--size",
        type=int,
        nargs="+",
        help="Size of the rectangle board. (default 9 x 9, min 3 x 3, min with UI 4 x 3)",
    )
    g2.add_argument(
        "--easy",
        action="store_true",
        help="9 x 9, 10 mines (default if no size is specified)",
    )
    g2.add_argument("--medium", action="store_true", help="16 x 16, 40 mines")
    g2.add_argument("--hard", action="store_true", help="30 x 16, 99 mines")
    g2.add_argument(
        "--impossible", action="store_true", help="50 x 50, 500 mines"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        type=int,
        choices=[0, 1, 2, 3],
        help="Level of verbosity. Default 0, 1 information about each level, 2 showing actions, 3 showing boards.",
    )
    parser.add_argument("--seed", default=None, type=int, help="Random seed.")
    return parser


def process_args(args: List[str] = []):
    """Parse arguments, check validity and return usefull values."""
    parser = get_parser()
    args = parser.parse_args(args + sys.argv[1:])

    if not args.agent and args.sim:
        parser.error("Can't simulate player.")
    if args.sim and args.sim < 1:
        parser.error("Invalid number of simulations.")
    if args.size and len(args.size) > 2:
        parser.error("Invalid size.")
    if (args.easy or args.medium or args.hard or args.impossible) and (
        args.density or args.mine_count
    ):
        parser.error("Can't specify mines in predefined levels.")
    if args.density and (args.density < 0 or args.density > 1):
        parser.error("Invalid density.")
    if args.mine_count and (
        args.mine_count < 0
        or (args.size and args.mine_count >= args.size[0] * args.size[1])
        or (not args.size and args.mine_count > 81)
    ):
        parser.error("Invalid number of mines.")

    agent = None
    if args.agent:
        try:
            spec = spec_from_file_location(
                f"agents.{str.lower(args.agent)}",
                path_join(AGENTS_DIR, f"{str.lower(args.agent)}.py"),
            )
            am = module_from_spec(spec)
            spec.loader.exec_module(am)
            agent: ArtificialAgent = getattr(am, args.agent)(args.verbose)
        except BaseException as e:
            parser.error(f"Invalid agent name:\n{str(e)}")

    if args.size:
        if len(args.size) == 1:
            width, height = args.size[0], args.size[0]
        else:
            width, height = args.size

        if width < 3 or height < 3:
            parser.error("Invalid size (too small).")

        if args.mine_count:
            mines = args.mine_count
        elif args.density:
            mines = round(width * height * args.density)
        else:
            mines = round(width * height * 0.2)
    elif args.medium:
        width, height, mines = 16, 16, 40
    elif args.hard:
        width, height, mines = 30, 16, 99
    elif args.impossible:
        width, height, mines = 50, 50, 500
    else:
        if args.mine_count is not None:
            width, height, mines = 9, 9, args.mine_count
        elif args.density is not None:
            width, height, mines = 9, 9, int(81 * args.density)
        else:
            width, height, mines = 9, 9, 10

    return agent, width, height, mines, args.seed, args.sim, args.verbose


def sim(
    agent: ArtificialAgent,
    width: int,
    height: int,
    mines: int,
    start_seed: Optional[int],
    sims: int,
    verbose: bool,
    gui,
) -> Tuple[float, int, int]:
    """
    Returns total_time, total_hints and total_wins.
    """
    total_time = 0
    total_hints = 0
    total_wins = 0
    print("board size is {0} x {1}, {2} mines".format(width, height, mines))
    end = False
    for seed in (
        range(start_seed, start_seed + sims)
        if start_seed is not None
        else random_sample(range(max(1000, sims)), sims)
    ):
        board = Board(width, height, mines, seed)
        board.suggest_safe_tile()
        hints = 1

        if agent:
            agent.new_game()
        if gui:
            gui.new_board(board)

        observed = 0
        running = True
        # GAME LOOP
        while running:
            # CHECK
            if board.is_victory():
                if gui:
                    end = not gui.wait_next()
                elif verbose:
                    print(
                        "seed {0}: solved in {1:.3f} s, hints = {2}".format(
                            seed, agent.think_time, hints
                        )
                    )
                total_hints += hints
                total_wins += 1

                if agent:
                    total_time += agent.think_time

                running = False
                continue

            if board.boom:
                if gui:
                    end = not gui.wait_next()
                elif verbose:
                    print(
                        "seed {0}: failed in {1:.3f} s, hints = {2}".format(
                            seed, agent.think_time, hints
                        )
                    )
                total_hints += hints

                if agent:
                    total_time += agent.think_time

                running = False
                continue

            # MOVE
            if agent:
                if not observed:
                    agent.observe(board.get_view())
                observed += 1
                action = agent.act()
            else:
                action = gui.choose_action()
                if action is None:
                    end = True
                    break

            if board.is_possible(action):
                if action.type == ActionFactory.SUGGEST_SAFE_TILE:
                    hints += 1
                board.apply_action(action)
                observed = 0
            else:
                print(
                    "WARNING: Ignoring invalid action: {}.".format(
                        ActionFactory.action_to_string(action)
                    )
                )

            # DRAW
            if gui:
                if not gui.draw_and_wait(board, bool(agent)):
                    end = True
                    break

            action = None

        if end:
            break

    if agent:
        print(
            "Average in {} rounds: time = {:.3f} s, hints = {:.1f}".format(
                sims,
                total_time / sims,
                total_hints / sims,
            )
        )
        if not gui:
            print(
                "Solved {} ({}%)".format(
                    total_wins,
                    total_wins / sims * 100,
                )
            )
    return (sims, total_time / sims, total_hints / sims)


def main(args: List[str] = []) -> Tuple[float, int, int]:
    agent, width, height, mines, seed, sims, verbose = process_args(args)

    # set ui if needed
    gui = None
    if sims is None:
        from game.mine_gui import MineGUI

        gui = MineGUI()
        sims = 100
    elif not agent:
        from game.mine_gui import MineGUI

        gui = MineGUI()

    if gui:
        if width < 4 or height < 3:
            raise RuntimeError("Board is too small for UI (minimum is 4 x 3).")
        if width > 45 or height > 22:
            raise RuntimeError("Board is too big for UI (maximum is 45 x 22).")

    return sim(agent, width, height, mines, seed, sims, verbose, gui)


if __name__ == "__main__":
    # if you don't want to specify arguments for the script you can also
    # call main with desired arguments in list
    # e.g. main(["--easy", "-s", "10"]), main(["--seed=1", "-a=Agent"])
    main()
