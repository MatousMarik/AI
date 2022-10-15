#!/usr/bin/env python3
import game.controllers as gc
from game.pacman import Game
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Tuple
from time import perf_counter
from random import randrange
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
        help=(
            "Agent to use, should be name of class in the file lowercase.py,"
            " in the same directory. (default player)"
        ),
    )
    parser.add_argument(
        "-s",
        "--sim",
        type=int,
        help="Simulate a series of games without visualization",
    )
    parser.add_argument(
        "-l", "--level", default=1, type=int, help="Starting level (1-4)."
    )
    parser.add_argument(
        "-t",
        "--time_limit",
        default=None,
        type=float,
        help="Set time limit in ms for agent tick (ms).",
    )
    parser.add_argument("--seed", type=int, help="Random seed.")
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="Verbose output.",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Scale the visualized game resolution [0.2; 3]. Use only if needed.",
    )
    return parser


def process_args(
    args: List[str] = [],
) -> Tuple[gc.PacManControllerBase, Namespace, bool]:
    """Parse arguments, check validity and return usefull values."""
    parser = get_parser()
    args = parser.parse_args(args + sys.argv[1:])

    if args.level is not None and (args.level < 1 or args.level > 4):
        parser.error("Invalid level number.")

    if args.agent:
        try:
            spec = spec_from_file_location(
                f"agents.{str.lower(args.agent)}",
                path_join(AGENTS_DIR, f"{str.lower(args.agent)}.py"),
            )
            am = module_from_spec(spec)
            spec.loader.exec_module(am)
            agent: gc.PacManControllerBase = getattr(am, args.agent)(
                verbose=args.verbose
            )
        except BaseException as e:
            parser.error(f"Invalid agent name:\n{str(e)}")
    else:
        agent: gc.PacManControllerBase = gc.PacManControllerBase(True)

    if args.time_limit is not None:
        if args.time_limit <= 0:
            parser.error("Invalid time limit - has to be greater than 0.")
        else:
            args.time_limit /= 1000

    if args.sim is not None:
        if args.sim < 1:
            parser.error("Invalid number of simulations.")
        if args.agent is None:
            parser.error("You have to specify agent with --sim.")
        visualize = False
    else:
        visualize = True
        if args.scale < 0.2:
            parser.error("Scale too small.")
        if args.scale > 3:
            parser.error("Scale too big.")

    return agent, args, visualize


def sim(agent: gc.PacManControllerBase, args: Namespace, gui) -> float:
    """
    Function for simulating pacman game, returns average score.

    If ui is provided simulation will be visualized.
    """
    seeds = (
        (
            [randrange(0, 999999999) for _ in range(args.sim)]
            if args.seed is None
            else list(range(args.seed, args.seed + args.sim))
        )
        if args.sim is not None
        else [args.seed]
    )
    # INIT GAME
    game = Game(seeds[0])
    game.new_game(level=args.level)

    # INIT CONTROLLERS
    pac_controller = agent
    pac_controller.reset(game)
    ghosts_controller = gc.GhostController()
    ghosts_controller.reset(game)
    no_action = gc.PacManAction()

    # VISUALIZED SIM
    if gui is not None:
        if args.verbose:
            ghosts_controller._debugging = gui  # class
        gui = gui(game, args.scale)
        gui.game_loop(pac_controller, ghosts_controller, args.time_limit)
        return

    score = 0
    total_time = 0
    level = 0
    ticks = 0
    total_max_tick = 0
    # SIM
    for seed in seeds:
        if args.verbose:
            print(f"Seed {seed}:")
        game.new_game(level=args.level, seed=seed)
        time = 0
        max_tick = 0
        while not game.game_over:
            start = perf_counter()
            pac_controller.tick(game)
            tick_time = perf_counter() - start
            max_tick = max(max_tick, tick_time)
            time += tick_time

            ghosts_controller.tick(game)

            # check time limit
            if args.time_limit and tick_time > args.time_limit:
                # took too long
                pac_action: gc.PacManAction = no_action
                no_action.reset()
                if args.verbose:
                    print(
                        f"   slow tick {game.total_ticks} - {(tick_time * 1000):.1f} ms."
                    )
            else:
                pac_action: gc.PacManAction = pac_controller.get_action()

            ghosts_actions: gc.GhostsActions = ghosts_controller.get_actions()

            game.advance_game(
                pac_action.direction,
                [ga.direction for ga in ghosts_actions.actions],
            )
        total_time += time
        total_max_tick = max(total_max_tick, max_tick)
        score += game.score
        level += game.current_level - args.level
        ticks += game.total_ticks

        if args.verbose:
            print(
                " result: level {:d}, score {:d} in {:.2f} ms (in {:d} ticks)\n\t average {:.2f} ms/tick; max {:.2f} ms/tick".format(
                    seed,
                    game.current_level,
                    game.score,
                    time * 1000,
                    game.total_ticks,
                    time / game.total_ticks * 1000,
                    max_tick * 1000,
                )
            )

    avg_score = score / args.sim
    print("Averages from {} games:".format(args.sim))
    print("  levels cleared: {:.1f}".format(level / args.sim))
    print("  score: {:.1f}".format(avg_score))
    print(
        "  time: {:.1f} ms/tick, {:.2f} s/level".format(
            total_time / ticks * 1000,
            total_time / (level + args.sim),
        ),
    )
    print("Max tick {:.2f} ms".format(total_max_tick * 1000))
    return avg_score


def main(args_list: list = []) -> float:
    agent, args, visualize = process_args(args_list)

    gui = None
    if visualize:
        from game.pac_gui import PacView

        gui = PacView

    return sim(agent, args, gui)


if __name__ == "__main__":
    # if you don't want to specify arguments for the script you can also
    # call main with desired arguments in list
    # e.g. main(["-a=MyAgent", "-l", "2", "--sim=3"])
    main()
