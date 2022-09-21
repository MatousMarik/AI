#!/usr/bin/env python3
from game.dino import Game, DinoMove, Coords
from game.agent import Agent
from argparse import ArgumentParser, Namespace
from importlib.util import spec_from_file_location, module_from_spec
from typing import List, Optional, Tuple
from time import perf_counter
from random import randrange
from os.path import join as path_join, dirname
import sys

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
        help="Set number of simulations of dino game. Set => no visualization.",
    )
    parser.add_argument(
        "-t",
        "--time_limit",
        default=None,
        type=float,
        help="Set strict time limit in ms for agent tick. (only for simulations)",
    )
    parser.add_argument("--seed", type=int, help="Random seed.")
    parser.add_argument(
        "-r",
        "--vis_rect",
        default=False,
        action="store_true",
        help="Visualize bounding boxes. (only for visualization)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="Debuging visualization (only for visualization).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        type=int,
        help="Level of verbosity: 0 for nothing, 1 for level info, 2 for agent info.",
    )
    return parser


def process_args(
    args: List[str] = [],
) -> Tuple[Agent, Namespace, bool]:
    """Parse arguments, check validity and return usefull values."""
    parser = get_parser()
    args = parser.parse_args(args + sys.argv[1:])

    agent: Agent = None
    if args.agent:
        try:
            spec = spec_from_file_location(
                f"agents.{str.lower(args.agent)}",
                path_join(AGENTS_DIR, f"{str.lower(args.agent)}.py"),
            )
            agent_module = module_from_spec(spec)
            spec.loader.exec_module(agent_module)
            # agent is a non-instantiated class
            agent = getattr(agent_module, args.agent)
            agent.verbose = args.verbose == 2
            agent.debug = args.debug
        except BaseException as e:
            parser.error(f"Invalid agent name.\n{str(e)}")

    if args.sim is not None:
        if args.sim < 1:
            parser.error("Invalid number of simulations.")
        if args.agent is None:
            parser.error("You have to specify Agent with --sim.")
        if args.time_limit is not None:
            if args.time_limit < 1:
                parser.error("Invalid time limit - has to be greater than 0.")
            else:
                # perf_counter returns time in seconds
                args.time_limit /= 1000
        visualize = False
    else:
        visualize = True

    return agent, args, visualize


def sim(agent: Agent, args: Namespace) -> None:
    """
    Simulate dino games with with given Agent and arguments.
    """
    seeds = (
        [randrange(0, 999999999) for _ in range(args.sim)]
        if args.seed is None
        else list(range(args.seed, args.seed + args.sim))
    )
    # CREATE GAME
    game: Game = Game(new_game=False)

    score = 0
    total_time = 0
    total_ticks = 0

    # SIM
    for seed in seeds:
        game.new_game(seed)

        time = 0
        ticks = 0
        time_fine = True
        while not game.game_over:
            ticks += 1
            start = perf_counter()
            move: DinoMove = agent.get_move(game)
            tick_time = perf_counter() - start
            time += tick_time

            # check strict time limit
            if args.time_limit and tick_time > args.time_limit:
                time_fine = False
                break

            game.tick(move)

        total_time += time
        score += game.score
        total_ticks += ticks

        if args.verbose > 0:
            time *= 1000
            if time_fine:
                fail_s = ""
            else:
                fail_s = " failed tick {} - {:.1f} ms".format(
                    ticks, tick_time * 1000
                )
            print(
                "Seed {}{}: score {} in {:.2f}ms, {:.2f} ms/tick".format(
                    seed,
                    fail_s,
                    game.score,
                    time,
                    time / ticks,
                )
            )

    avg_score = score / args.sim
    print("Averages from {} games:".format(args.sim))
    print("  score: {:.1f}".format(avg_score))
    print("  time: {:.1f} ms/tick".format(total_time / total_ticks * 1000))


def main(args_list: list = []) -> None:
    agent, args, visualize = process_args(args_list)

    gui = None
    if visualize:
        from game.dino_gui import Dino_GUI
        from game.debug_game import DebugGame

        if args.debug:
            game = DebugGame(args.seed)
            add_initial_debug_visualization(game)
            gui = Dino_GUI(agent, game, args.vis_rect, debug=True)
        else:
            gui = Dino_GUI(agent, Game(args.seed), args.vis_rect)
        gui.play()
    else:
        sim(agent, args)


def add_initial_debug_visualization(game) -> None:
    """
    Initialize visual debugging if needed.

    Can be used for marking distances.
    """
    # intellisense hack
    from game.dino_gui import DebugGame

    game: DebugGame = game

    # t = game.add_text(Coords(10, 10), "red", "Text")
    # t.text = "Hello World"
    # game.add_dino_rect(Coords(-10, -10), 150, 150, "yellow")
    # l = game.add_dino_line(Coords(0, 0), Coords(100, 0), "black")
    # l.dxdy.update(50, 30)
    # l.dxdy.x += 50
    # game.add_moving_line(Coords(1000, 100), Coords(1000, 500), "purple")


if __name__ == "__main__":
    # if you don't want to specify arguments for the script you can also
    # call main with desired arguments in list
    # e.g. main(["-a", "Agent", "--seed", "42", "-s", "10", "-v"]),
    # or shorter: main(["-a=Agent", "--se=0", "--vis", "--d"])
    main()
