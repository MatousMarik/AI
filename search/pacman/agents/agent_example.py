#!/usr/bin/env python3
from game.controllers import PacManControllerBase
from game.pacman import Game, DM


class Agent_Example(PacManControllerBase):
    """
    Go after nearest pill and show how to use visualization.

    Comment/un-comment code as desired,
    drawing all would probably be too much.
    """

    def tick(self, game: Game) -> None:
        current = game.pac_loc
        active_pills = game.get_active_pills_nodes()
        active_power_pills = game.get_active_power_pills_nodes()
        targets = active_pills + active_power_pills

        nearest = game.get_target(current, targets, True, DM.PATH)

        # # EXAMPLE OF VISUAL DEBUGGING
        # from game.pac_gui import PacView

        # # add the path that pac-man is following
        # PacView.add_points(game, "green", game.get_path(current, nearest))

        # # add the path from pac-man to the nearest existing power pill
        # nearest_pp = game.get_target(current, active_power_pills, True, DM.PATH)
        # PacView.add_points(game, "cyan", game.get_path(current, nearest_pp))

        # # write ghost distances
        # ghost_distances = [
        #     game.get_path_distance(current, ghost_loc)
        #     for ghost_loc in game.ghost_locs
        # ]
        # ghost_distances = [
        #     game.get_path_distance(current, game.get_ghost_loc(g))
        #     for g in range(game.NUM_GHOSTS)
        # ]
        # PacView.add_text_xy(
        #     "greenyellow",
        #     0,
        #     0,
        #     "Ghost distances: " + ", ".join((str(d) for d in ghost_distances)),
        # )

        # # add the path AND ghost path from Ghost 0 to the first power pill
        # # (to illustrate the differences)
        # if game.get_lair_time(0) == 0:
        #     pill_loc = game.get_node_indices_with_power_pills()[0]
        #     PacView.add_points(
        #         game, "orange", game.get_path(game.get_ghost_loc(0), pill_loc)
        #     )
        #     PacView.add_points(game, "yellow", game.get_ghost_path(0, pill_loc))

        # # add the path from Ghost 1 to the closest power pill
        # if game.get_lair_time(1) == 0:
        #     PacView.add_points(
        #         game,
        #         "white",
        #         game.get_ghost_path(
        #             1,
        #             game.get_ghost_target(
        #                 1, game.get_node_indices_with_power_pills(), True
        #             ),
        #         ),
        #     )

        # # add lines connecting pac-man and the power pills
        # PacView.add_lines(
        #     game,
        #     "cyan",
        #     [current] * len(active_power_pills),
        #     game.get_active_power_pills_nodes(),
        # )

        # # add lines to the ghosts (if not in lair) - green if edible else red
        # for g in range(game.NUM_GHOSTS):
        #     if game.get_lair_time(g) == 0:
        #         PacView.add_lines(
        #             game,
        #             "green" if game.is_edible(g) else "red",
        #             [current],
        #             [game.get_ghost_loc(g)],
        #         )

        # # add the paths the ghost would need to follow to reach pac-man
        # for g, c in zip(
        #     range(game.NUM_GHOSTS), ["red", "blue", "magenta", "orange"]
        # ):
        #     if game.get_lair_time(g) == 0:
        #         PacView.add_points(game, c, game.get_ghost_path(g, current))

        self.pacman.set(game.get_next_pacman_dir(nearest, True, DM.PATH))
