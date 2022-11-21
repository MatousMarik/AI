#!/usr/bin/env python3
from time import perf_counter
from game.cells import Game
from game.agent import Agent
from argparse import ArgumentParser, Namespace
from random import Random
from importlib.util import spec_from_file_location, module_from_spec
import sys

from typing import Optional, Tuple, List, Union

from os.path import join as path_join, dirname

AGENTS_DIR = path_join(dirname(__file__), "agents")


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "agent1", nargs="?", type=str, help="Name of the first player agent."
    )
    parser.add_argument(
        "agent2",
        nargs="?",
        type=str,
        help="Name of the second player agent."
        + " (If not specified and visualized, player plays.)",
    )
    parser.add_argument(
        "-c",
        "--num_cells",
        default=[20, 50],
        type=int,
        nargs="+",
        help="Number of cells in the game. Can be value or range"
        + " from which will be randomly chosen. (default [20, 50])",
    )
    parser.add_argument(
        "-d",
        "--density",
        default=0.75,
        type=float,
        help="Density of cells on board. (default 0.75)",
    )
    parser.add_argument(
        "-p",
        "--hole_probability",
        type=float,
        default=0.8,
        help="Probability that distant cells won't be connected. (default 0.8)",
    )
    parser.add_argument(
        "-s",
        "--sim",
        type=int,
        help="Simulate a series of games without visualization.",
    )
    parser.add_argument(
        "-m",
        "--max_turns",
        default=200,
        type=int,
        help="Set maximal number of turns. (default 500)",
    )
    parser.add_argument(
        "-t",
        "--time_limit",
        default=None,
        type=float,
        help="Set strict time limit in s for agents tick. (only for simulations)",
    )
    parser.add_argument(
        "--agent2_first",
        default=False,
        action="store_true",
        help="Agent2 starts.",
    )
    parser.add_argument(
        "--swap",
        default=False,
        action="store_true",
        help="Change first agent after each game.",
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
        "--scale", type=float, default=1, help="Scale visualization window."
    )
    return parser


def process_args(
    args: List[str] = [],
) -> Tuple[Agent, Agent, Union[None, Agent], bool, Namespace]:
    """
    Parse arguments, check validity and return useful values.

    Return:
    * instance of agent1
    * instance of agent2
    * instance of player agent
    * visualize?
    * args
    """
    parser = get_parser()
    args = parser.parse_args(args + sys.argv[1:])

    if args.scale < 0.3 or args.scale > 5:
        parser.error("Invalid scale. Use values from [0.3, 5]")

    if args.max_turns is not None:
        if args.max_turns <= 0:
            parser.error("Invalid number of turns.")
    else:
        args.max_turns = -1

    if not 0.2 <= args.density <= 1:
        parser.error("Invalid density, should be from [0.2, 1].")

    if not 0 <= args.hole_probability <= 1:
        parser.error("Invalid hole probability, should be from [0, 1].")

    gui_agent = None
    agent2: Agent = None
    if args.agent2:
        try:
            spec = spec_from_file_location(
                f"agents.{str.lower(args.agent2)}",
                path_join(AGENTS_DIR, f"{str.lower(args.agent2)}.py"),
            )
            am = module_from_spec(spec)
            spec.loader.exec_module(am)
            agent2 = getattr(am, args.agent2)()
            agent2.init_random(None if args.seed is None else args.seed + 1)
            agent2.verbose = args.verbose
        except BaseException as e:
            parser.error(f"Invalid agent name. \n{str(e)}")
    else:
        from game.cells_gui import CellsGUIAgent

        agent2 = CellsGUIAgent(args.scale)
        gui_agent = agent2

    if args.agent1:
        try:
            spec = spec_from_file_location(
                f"agents.{str.lower(args.agent1)}",
                path_join(AGENTS_DIR, f"{str.lower(args.agent1)}.py"),
            )
            am = module_from_spec(spec)
            spec.loader.exec_module(am)
            agent1: Agent = getattr(am, args.agent1)()
            agent1.init_random(args.seed)
            agent1.verbose = args.verbose
        except BaseException as e:
            parser.error(f"Invalid agent name. \n{str(e)}")
    else:
        agent1 = agent2

    if args.sim is not None:
        if args.sim < 1:
            parser.error("Invalid number of simulations.")
        if args.agent2 is None:
            parser.error("You have to specify both agents with --sim.")
        if args.time_limit is not None:
            if args.time_limit <= 0:
                parser.error("Invalid time limit - has to be greater than 0.")
            else:
                # perf_counter returns time in seconds
                args.time_limit
        visualize = False
    else:
        visualize = True

    return agent1, agent2, gui_agent, visualize, args


def sim(
    agent1: Agent,
    agent2: Agent,
    args: Namespace,
) -> Tuple[int, int, int]:
    game = Game(args.seed, args.max_turns)
    if args.agent1 == args.agent2:
        agent_names = (None, args.agent1 + "1", args.agent2 + "2")
    else:
        agent_names = (None, args.agent1, args.agent2)
    if len(args.num_cells) == 1:
        nc = args.num_cells[0]
        get_num_cells = lambda: nc
    else:
        r = Random(args.seed)
        mi, ma = args.num_cells[:2]
        get_num_cells = lambda: r.randrange(mi, ma)

    agents = (None, agent1, agent2)
    ais = (0, 2, 1) if args.agent2_first else (0, 1, 2)
    total_times = [None, 0, 0]
    total_max_times = [None, 0, 0]
    total_wins = [0, 0, 0]
    total_timeouts = [None, 0, 0]
    total_rounds = [None, 0, 0]

    for gi in range(args.sim):
        if not args.swap or gi % 2 == 0:
            num_cells = get_num_cells()
        game.new_game(num_cells, args.density, args.hole_probability)
        times = [None, 0, 0]
        max_times = [None, 0, 0]
        time_bad = 0
        running = True
        while True:
            for ai in ais[1:]:
                agent = agents[ai]
                start = perf_counter()
                move = agent.get_move(game.clone())
                tick_time = perf_counter() - start
                max_times[ai] = max(max_times[ai], tick_time)
                times[ai] += tick_time
                if args.time_limit and tick_time > args.time_limit:
                    time_bad = ai
                    running = False
                    break

                game.make_move(move)
                if game.winner != -1:
                    running = False
                    break
            if not running:
                break
            game.grow_cells()

        for i in (1, 2):
            total_rounds[i] += game.get_player_round(ais[i])
            times[i] *= 1000
            total_times[i] += times[i]
            max_times[i] *= 1000
            total_max_times[i] = max(total_max_times[i], max_times[i])

        if time_bad:
            total_wins[3 - time_bad] += 1
            total_timeouts[time_bad] += 1
            if args.verbose:
                print(
                    "{}: agent {} exceeded time - ({:.1f}) ms at round {}.".format(
                        gi, time_bad, tick_time * 1000, game.round
                    )
                )
        else:
            total_wins[ais[game.winner]] += 1
            if args.verbose:
                if game.winner == 0:
                    print("{}: draw in {} rounds.".format(gi, game.round))
                else:
                    print(
                        "{}: agent {} won in {} rounds.".format(
                            gi, agent_names[ais[game.winner]], game.round
                        )
                    )
        if args.verbose:
            print(
                "{}a1: {:.2f} ms => {:.2f} ms/round, max {:.2f} ms/round".format(
                    " " * (len(str(gi)) + 2),
                    times[1],
                    times[1] / game.get_player_round(1),
                    max_times[1],
                )
            )
            print(
                "{}a2: {:.2f} ms => {:.2f} ms/round, max {:.2f} ms/round".format(
                    " " * (len(str(gi)) + 2),
                    times[2],
                    times[2] / game.get_player_round(2),
                    max_times[2],
                )
            )
        if args.swap:
            ais = (0, *ais[:0:-1])
    off = len(agent_names[1]) - len(agent_names[2])
    if off > 0:
        names = None, agent_names[1], agent_names[2] + " " * off
    else:
        names = None, agent_names[1] + " " * (-off), agent_names[2]
    off = len(str(total_wins[1])) - len(str(total_wins[2]))
    if off > 0:
        pre_wins = None, "", " " * off
    else:
        pre_wins = None, " " * -off, ""

    print("Results from {} games:".format(args.sim))
    for i in range(1, 3):
        print(
            "{} won {}{} game{} ({:2.0f}%), had {} timeout{}, with average {:.1f} ms/round, max {:.1f} ms/round.".format(
                names[i],
                pre_wins[i],
                total_wins[i],
                "" if total_wins[i] == 1 else "s",
                total_wins[i] / args.sim * 100,
                total_timeouts[i],
                "" if total_timeouts[i] == 1 else "s",
                total_times[i] / total_rounds[i],
                total_max_times[i],
            )
        )
    print(
        "draw {}x ({:.0f}%)".format(
            total_wins[0], total_wins[0] / args.sim * 100
        )
    )
    return tuple(total_wins)


def sim_with_gui(agent1: Agent, agent2: Agent, gui, args: Namespace) -> None:
    from game.cells_gui import CellsGUI

    names = [None, args.agent1, args.agent2 if args.agent2 else "Player"]
    if names[1] == names[2]:
        names[1] += "1"
        names[2] += "2"
    # intellisense hack
    gui: CellsGUI = gui
    game = Game(args.seed, args.max_turns)
    if len(args.num_cells) == 1:
        nc = args.num_cells[0]
        get_num_cells = lambda: nc
    else:
        r = Random(args.seed)
        mi, ma = args.num_cells[:2]
        get_num_cells = lambda: r.randrange(mi, ma)

    agents = (None, agent1, agent2)
    ais = [2, 1] if args.agent2_first else [1, 2]
    play = True
    while play:
        game.new_game(get_num_cells(), args.density, args.hole_probability, gui)
        running = True
        while True:
            gui.draw_cells(*game.get_gui_info())
            for ai in ais:
                agent = agents[ai]
                move = agent.get_move(game.clone())
                if agent is not gui:
                    if not gui.wait_next():
                        return

                    gui.draw_transfers(move, game.turn)
                game.make_move(move)
                if agent is not gui and not gui.wait_next():
                    return

                gui.draw_cells(*game.get_gui_info())

                if game.winner != -1:
                    running = False
                    if not gui.wait_next():
                        return
                    play = gui.draw_end_and_wait(names[game.winner])
                    break
            if not running:
                break
            game.grow_cells()

        if args.swap:
            ais[:] = ais[::-1]


def main(args_list: list = []) -> Union[Tuple[int, int, int], None]:
    agent1, agent2, gui_agent, visualize, args = process_args(args_list)

    if visualize:
        if gui_agent:
            gui = agent2
        else:
            from game.cells_gui import CellsGUI

            gui = CellsGUI(args.scale)
        sim_with_gui(agent1, agent2, gui, args)
    else:
        return sim(agent1, agent2, args)


if __name__ == "__main__":
    # if you don't want to specify arguments for the script you can also
    # call main with desired arguments in list
    # e.g. main(["Ranger", "MyAgent", "-m=10", "-s 10"])
    main()
