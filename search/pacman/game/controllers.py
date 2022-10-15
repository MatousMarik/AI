#!/usr/bin/env python3
from game.pacman import Game, Direction
from typing import List, Optional, Sequence, Tuple
from copy import deepcopy
from enum import IntEnum
from math import isclose
from random import Random


def get_euclidean_distance_sq(x1, y1, x2, y2) -> float:
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


class Action:
    def __init__(self):
        self.direction: int = Direction.NONE

    def left(self) -> None:
        self.direction = Direction.LEFT

    def right(self) -> None:
        self.direction = Direction.RIGHT

    def down(self) -> None:
        self.direction = Direction.DOWN

    def up(self) -> None:
        self.direction = Direction.UP

    def set(self, dir: int) -> None:
        self.direction = Direction(dir)

    def get(self) -> int:
        return Direction(self.direction)

    def clone(self) -> "Action":
        return deepcopy(self)

    def reset(self) -> None:
        self.direction = -1


class PacManAction(Action):
    def __init__(self):
        super().__init__()
        self.pause_simulation: bool = False
        self.next_frame: bool = False

    def pause(self) -> None:
        self.pause_simulation = True

    def resume(self) -> None:
        self.pause_simulation = False

    def toggle_pause(self) -> None:
        self.pause_simulation = not self.pause_simulation

    def reset(self) -> None:
        super().reset()
        self.pause_simulation = False


class GhostsActions:
    def __init__(self, ghost_count: int = 4):
        self.ghost_count: int = ghost_count
        self.actions: List[Action] = [Action() for _ in range(ghost_count)]
        self.pause_simulation: bool = False
        self.next_frame: bool = False

    def __getitem__(self, ghost_index: int) -> Action:
        self.actions[ghost_index]

    def set(self, directions: List[int]) -> None:
        for a, d in zip(self.actions, directions):
            a.direction = d

    def blinky(self) -> Action:
        return self.actions[0]

    def pinky(self) -> Action:
        return self.actions[1]

    def clyde(self) -> Action:
        return self.actions[2]

    def inky(self) -> Action:
        return self.actions[3]

    def pause(self) -> None:
        self.pause_simulation = True

    def resume(self) -> None:
        self.pause_simulation = False

    def toggle_pause(self) -> None:
        self.pause_simulation = not self.pause_simulation

    def reset(self) -> None:
        for a in self.actions:
            a.reset()
        self.pause_simulation = False
        self.next_frame = False


class GhostController:
    NUM_SCATTERS_PER_LEVEL = 4
    SCATTER = 0
    CHASE = 1
    FRIGHTENED = 2

    GHOST_COUNT = 4

    class GhostAI:
        BLINKY = 0
        PINKY = 1
        CLYDE = 2
        INKY = 3

        CORNER = (0, 0)
        PINK_DIST = 16
        TILE_DIST = 4

        BLINKY_CORNER_NODE = 0
        PINKY_CORNER_NODE = 76
        CLYDE_CORNER_NODE = 1195
        INKY_CORNER_NODE = 1290

        CLYDE_MAINTAIN_DISTANCE = 8
        CLYDE_DISTANCE_SQ = (CLYDE_MAINTAIN_DISTANCE * TILE_DIST) ** 2
        INKY_PAC_DISTANCE = 2

        def __init__(self, game: Game) -> None:
            self.corners: List[Tuple[int, int]] = [
                game.get_xy(self.BLINKY_CORNER_NODE),
                game.get_xy(self.PINKY_CORNER_NODE),
                game.get_xy(self.CLYDE_CORNER_NODE),
                game.get_xy(self.INKY_CORNER_NODE),
            ]

        def target_frightened(self, ghost: int, game: Game) -> None:
            return None

        def target_chase(self, ghost: int, game: Game) -> Tuple[int, int]:
            target = game.get_xy(game.pac_loc)
            if ghost == self.PINKY:
                pac_last_direction = game.pac_dir
                if pac_last_direction == Direction.UP:
                    return tuple(t - self.PINK_DIST for t in target)
                elif pac_last_direction == Direction.LEFT:
                    return target[0] - self.PINK_DIST, target[1]
                elif pac_last_direction == Direction.RIGHT:
                    return target[0] + self.PINK_DIST, target[1]
                elif pac_last_direction == Direction.DOWN:
                    return target[0], target[1] + self.PINK_DIST
            elif ghost == self.CLYDE:
                distance_from_pac = get_euclidean_distance_sq(
                    *game.get_xy(game._ghost_locs[ghost]), *target
                )
                if distance_from_pac < self.CLYDE_DISTANCE_SQ:
                    return self.corners[ghost]
            elif ghost == self.INKY:
                pac_dir = game.pac_dir
                if pac_dir == Direction.UP:
                    tx, ty = (
                        target[0] - self.TILE_DIST * self.INKY_PAC_DISTANCE,
                        target[1] - self.TILE_DIST * self.INKY_PAC_DISTANCE,
                    )
                elif pac_dir == Direction.LEFT:
                    tx, ty = (
                        target[0] - self.TILE_DIST * self.INKY_PAC_DISTANCE,
                        target[1],
                    )
                elif pac_dir == Direction.RIGHT:
                    tx, ty = (
                        target[0] + self.TILE_DIST * self.INKY_PAC_DISTANCE,
                        target[1],
                    )
                elif pac_dir == Direction.DOWN:
                    tx, ty = (
                        target[0],
                        target[1] + self.TILE_DIST * self.INKY_PAC_DISTANCE,
                    )
                else:
                    tx, ty = target
                bx, by = game.get_xy(game._ghost_locs[ghost])
                return 2 * tx - bx, 2 * ty - by
            return target

        def target_scatter(
            self, ghost: int, game: Game
        ) -> Optional[Tuple[int, int]]:
            if ghost == self.BLINKY:
                if game.get_active_pills_count() < 20:
                    return game.get_xy(game.pac_loc)
            return self.corners[ghost]

    def __init__(self, FPS: int = 25):
        self.actions: GhostsActions = GhostsActions(self.GHOST_COUNT)

        self.FPS: int = FPS
        self.state_change_time: int = 0
        self.state_change_shift_time: int = 0
        self.number_of_scatter: int = 0
        self.number_of_chase: int = 0

        self.global_state: int = 0
        self.prev_state: int = 0

        self.ghost_state: List[int] = None

        self.ai: GhostController.GhostAI = None

        self._debugging = None

    def reset(self, game: Game) -> None:
        self.actions.reset()
        self.ai = GhostController.GhostAI(game)

        self.state_change_time = game.total_ticks
        self.state_change_shift_time = self.state_change_time + 175
        self.number_of_scatter = 0
        self.number_of_chase = 0

        self.global_state = self.SCATTER

        self.ghost_state = [self.SCATTER] * self.GHOST_COUNT

    def get_actions(self) -> GhostsActions:
        return self.actions

    def tick(self, game: Game) -> None:
        if game.level_ticks <= 10:
            self.number_of_scatter = 0
            self.number_of_chase = 0
            self.state_change_shift_time = game.total_ticks

        state_change_timer = self.state_change_shift_time - game.total_ticks
        if (
            state_change_timer < 0
            and self.number_of_scatter < self.NUM_SCATTERS_PER_LEVEL
        ):
            next_state_time_in_sec = 0
            if self.global_state == self.SCATTER:
                self.global_state = self.CHASE
                self.number_of_scatter += 1

                if game.current_level < 5:
                    if game.current_level == 1:
                        next_state_time_in_sec = 20
                    else:
                        if self.number_of_chase < 2:
                            next_state_time_in_sec = 20
                        else:
                            next_state_time_in_sec = 1033
                else:
                    if self.number_of_chase < 2:
                        next_state_time_in_sec = 20
                    else:
                        next_state_time_in_sec = 1037
            else:
                self.global_state = self.SCATTER
                if game.current_level < 5:
                    if game.current_level == 1:
                        if self.number_of_scatter < 2:
                            next_state_time_in_sec = 7
                        else:
                            next_state_time_in_sec = 5
                    else:
                        if self.number_of_scatter < 2:
                            next_state_time_in_sec = 7
                        elif self.number_of_scatter == 2:
                            next_state_time_in_sec = 5
                        else:
                            next_state_time_in_sec = 1
                else:
                    if self.number_of_scatter <= 2:
                        next_state_time_in_sec = 5
                    else:
                        next_state_time_in_sec = 1
                self.number_of_chase += 1

            self.state_change_shift_time = (
                game.total_ticks + next_state_time_in_sec * self.FPS
            )

            # rewrite direction
            for a in self.actions.actions:
                a.direction = 3
            return

        for g in range(self.GHOST_COUNT):
            if game.get_edible_time(g) > 0:
                self.ghost_state[g] = self.FRIGHTENED
            else:
                self.ghost_state[g] = self.global_state

            gs = self.ghost_state[g]
            if gs == self.SCATTER:
                ghost_target = self.ai.target_scatter(g, game)
            elif gs == self.CHASE:
                ghost_target = self.ai.target_chase(g, game)

            chosen_dir = -1
            if game.ghost_requires_action(g):
                p_dirs = game.get_possible_ghost_dirs(g)
                if gs != self.FRIGHTENED:
                    chosen_direction_distance = 100_000_000_000.0
                    equal_paths_check = False
                    for dir in p_dirs:
                        dir_node_num = game.get_neighbor(
                            game._ghost_locs[g], dir
                        )
                        distance_between_neighbor = get_euclidean_distance_sq(
                            *game.get_xy(dir_node_num), *ghost_target
                        )

                        if isclose(
                            distance_between_neighbor, chosen_direction_distance
                        ):
                            equal_paths_check = True
                        elif (
                            distance_between_neighbor
                            < chosen_direction_distance
                        ):
                            equal_paths_check = False
                            chosen_direction_distance = (
                                distance_between_neighbor
                            )
                            chosen_dir = dir

                    if equal_paths_check:
                        left_priority = False
                        for dir in p_dirs:
                            if dir == 0:  # UP
                                chosen_dir = 0
                                break
                            elif dir == 3:  # LEFT
                                chosen_dir = 3
                                left_priority = True
                            elif dir == 2 and not left_priority:  # DOWN
                                chosen_dir = 2
                else:  # FRIGHTENED STATE
                    if p_dirs:
                        chosen_dir = game._rnd.choice(p_dirs)
            self.actions.actions[g].direction = chosen_dir


class ValidKeys(IntEnum):
    """Key values from pygame."""

    UP = 1073741906
    RIGHT = 1073741903
    DOWN = 1073741905
    LEFT = 1073741904

    H = 104
    P = 112
    N = 110


VALID_KEYS = set(ValidKeys._value2member_map_.keys())


class PacManControllerBase:
    def __init__(
        self, human: bool = False, seed: int = 0, verbose: bool = False
    ) -> None:
        self.pacman: PacManAction = PacManAction()
        self.human: PacManAction = PacManAction()

        self.random = Random(seed)

        self.game: Game = None
        self.hijacked: bool = human

        # for debugging purposes only
        self.verbose: bool = verbose

    def reset(self, game: Game) -> None:
        self.pacman.reset()
        self.human.reset()
        self.game = game

    def get_action(self) -> PacManAction:
        return self.human if self.hijacked else self.pacman

    def press_key(self, key: int):
        if self.hijacked:
            if key == ValidKeys.UP:
                self.human.up()
            elif key == ValidKeys.DOWN:
                self.human.down()
            elif key == ValidKeys.LEFT:
                self.human.left()
            elif key == ValidKeys.RIGHT:
                self.human.right()
        if key == ValidKeys.H:
            self.hijacked = not self.hijacked
            if self.hijacked:
                self.human.pause_simulation = self.pacman.pause_simulation
        if key == ValidKeys.P:
            if self.hijacked:
                self.human.toggle_pause()
            else:
                self.pacman.toggle_pause()
        if key == ValidKeys.N:
            a = self.get_action()
            if a.pause_simulation:
                a.next_frame = True

    def tick(self, game: Game) -> None:
        pass
