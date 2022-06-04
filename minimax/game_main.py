#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentError
import re
from time import perf_counter as time_counter
from minimax_templates import Strategy, RandomStrategy, AbstractGame, GameUI
from typing import Optional, List
from importlib.util import spec_from_file_location, module_from_spec
from os.path import join as path_join
from os.path import dirname
import sys

from minimax import Minimax

from mcts import Mcts

DIR = dirname(__file__)

# {game_name: GameClass,
#             (ui module name, ui module path, UiClass),
#             {strategy_name: strategy_class}
#             [nonstandart (no MCTS/Minimax) strategies names]
# }
GAMES = {
    "tictactoe": (
        "TicTacToeGame",
        (
            "tictactoe.tictactoe_gui",
            path_join("tictactoe", "tictactoe_gui.py"),
            "TicTacToeGUI",
        ),
        {
            "random": RandomStrategy,
            "basic": "BasicStrategy",
            "minimax": Minimax,
            "mcts": Mcts,
        },
        ["random", "basic"],
    ),
    "trivial": (
        "TrivialGame",
        (
            "trivial.trivial_ui",
            path_join("trivial", "trivial_ui.py"),
            "TrivialUI",
        ),
        {
            "random": "RandomStrategy",
            "perfect": "PerfectStrategy",
            "minimax": Minimax,
            "mcts": Mcts,
        },
        ["random", "perfect"],
    ),
    "connect_four": (
        "ConnectFourGame",
        (
            "connect_four.connect_four_gui",
            path_join("connect_four", "connect_four_gui.py"),
            "ConnectFourGUI",
        ),
        {
            "random": RandomStrategy,
            "basic": "BasicStrategy",
            "heuristic": "HeuristicStrategy",
            "minimax": Minimax,
            "mcts": Mcts,
        },
        ["random", "basic", "heuristic"],
    ),
}


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        epilog="All available strategies are random, basic, perfect, heuristic, minimax, mcts."
    )

    # strategy regex
    pattern = re.compile(
        r"^(random|basic|perfect|heuristic|minimax|mcts)(:([0-9]+)(/(random|basic|perfect|heuristic))?)?$"
    )

    def regex_strategy(arg_value):
        """
        Pattern match strategy and its arguments.
        """
        r = pattern.match(arg_value)
        if not r:
            parser.error(
                ArgumentError(
                    message="Invalid strategy, should be one of {random, basic, perfect, heuristic, minimax, mcts}."
                )
            )
        else:
            if r[1] not in ["minimax", "mcts"]:
                if r[2] is not None:
                    parser.error("Cant specify details for this strategy.")
                else:
                    return [r[1]]
            elif r[1] == "minimax":
                if r[4] is not None:
                    parser.error("Cant specify base_strategy for minimax.")
                elif r[2] is None:
                    parser.error(
                        "Must specify depth for minimax.\nUse minimax:[depth]."
                    )
                else:
                    return [r[1], int(r[3])]
            else:
                if r[4] is None:
                    parser.error(
                        "Must specify iterations and base_strategy for mcts.\nUse mcts:[iterations]/[base_strategy]."
                    )
                else:
                    return [r[1], int(r[3]), r[5]]

    parser.add_argument(
        "game", type=str, choices=list(GAMES), help="Game to run."
    )
    parser.add_argument(
        "strategy1",
        type=regex_strategy,
        help="Strategy of the first player - bot.",
    )
    parser.add_argument(
        "strategy2",
        nargs="?",
        type=regex_strategy,
        help="Strategy of the second player. If not specified user will play vs first strategy.",
    )
    parser.add_argument(
        "-s",
        "--sim",
        default=None,
        type=int,
        help="Simulate a series of games without visualization.",
    )
    parser.add_argument("--seed", default=None, type=int, help="Random seed.")
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="Verbose output.",
    )
    return parser


def process_args(args: List[str] = []):
    """Parse arguments, check validity and return usefull values."""
    parser = get_parser()
    args = parser.parse_args(args + sys.argv[1:])

    game, ui, available_strats, base_strats = GAMES[args.game]

    try:
        spec = spec_from_file_location(
            f"{args.game}.{args.game}",
            path_join(DIR, args.game, f"{args.game}.py"),
        )
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        game = getattr(module, game)()
    except BaseException as e:
        parser.error(f"Specified module not working: \n{str(e)}")

    strategies = []
    ss = [args.strategy1]
    if args.strategy2 is not None:
        ss.append(args.strategy2)

    for s in ss:
        if s[0] not in available_strats:
            parser.error(
                f"'{s[0]}' is not available strategy for '{args.game}'"
            )

        if len(s) > 1:
            if s[1] < 0:
                parser.error(
                    "'{0}' is not valid {1}".format(
                        s[1],
                        "depth"
                        if s[0] == "minimax"
                        else "number of iterations",
                    )
                )

            if s[0] == "minimax":
                strategies.append(Minimax(game, s[1]))
            elif s[0] == "mcts":
                if s[2] not in base_strats:
                    parser.error(
                        f"'{s[2]}' is not valid base strategy for mcts in '{args.game}'. Use one of {base_strats}"
                    )
                AVS = available_strats[s[2]]
                if isinstance(AVS, str):
                    AVS = getattr(module, AVS)
                strategies.append(Mcts(game, AVS(), s[1]))
            else:
                parser.error(
                    f"Invalid strategy with specified details - '{s[0]}'"
                )
        else:
            AVS = available_strats[s[0]]
            if isinstance(AVS, str):
                AVS = getattr(module, AVS)
            strategies.append(AVS())

    if len(strategies) == 1:
        return args, game, ui, strategies[0], None
    else:
        return args, game, ui, strategies[0], strategies[1]


def sim(
    game: AbstractGame,
    strat1: Strategy,
    strat2: Strategy,
    count: int,
    start_seed: int,
    verbose: bool,
):
    wins = [0] * 3
    time = [0] * 3
    total_moves = [0] * 3

    name1 = type(strat1).__name__
    name2 = type(strat2).__name__

    for i in range(count):
        # shows progress
        if not verbose and (i * 10 / count) % 1 == 0:
            c = i * 10 // count
            print("|" + "\u25A0" * c + " " * (10 - c) + "|")

        seed = start_seed + i
        strat1.set_seed(seed)
        strat2.set_seed(seed + 1_000_000)
        s = game.initial_state(seed)
        moves = 0
        while not game.is_done(s):
            player = game.player(s)
            start = time_counter()
            a = strat1.action(s) if player == 1 else strat2.action(s)
            time[player] += (time_counter() - start) * 1000

            game.apply(s, a)
            moves += 1
            total_moves[player] += 1

        if verbose:
            print(f"seed {seed}: ", end="")
        o = game.outcome(s)
        if o == AbstractGame.DRAW:
            wins[0] += 1
            if verbose:
                print("draw", end="")
        elif o > AbstractGame.DRAW:
            wins[1] += 1
            if verbose:
                print(f"{name1} won", end="")
        else:
            wins[2] += 1
            if verbose:
                print(f"{name2} won", end="")
        if verbose:
            print(f" in {moves} moves")

    print(f"{name1} won {wins[1]} ({100 * wins[1] / count}%)")
    if wins[0] > 0:
        print(f"{wins[0]} draws ({100 * wins[0] / count}%)")
    print(f"{name2} won {wins[2]} ({100 * wins[2] / count}%)")

    if verbose:
        print(
            "{} took {:.3f} ms/move, {} took {:.3f} ms/move".format(
                name1, time[1] / total_moves[1], name2, time[2] / total_moves[2]
            )
        )
    return wins


def main(args_: List[str] = []) -> None:
    args, game, ui, strategy1, strategy2 = process_args(args_)
    if args.sim is not None:
        sim(
            game,
            strategy1,
            strategy2,
            args.sim,
            args.seed if args.seed is not None else 0,
            args.verbose,
        )
    else:
        try:
            spec = spec_from_file_location(ui[0], path_join(DIR, ui[1]))
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            UI = getattr(module, ui[2])
        except BaseException as e:
            raise RuntimeError(f"UI module not working: \n{str(e)}")

        ui: GameUI = UI(
            strategy1, strategy2, args.seed if args.seed is not None else 0
        )
        ui.play_loop()


if __name__ == "__main__":
    # if you don't want to specify arguments for the script you can also
    # call main with desired arguments in list
    # e.g. main(["trivial", "random", "mcts:20/random", "-s 10"])
    main()
