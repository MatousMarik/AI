#!/usr/bin/env python3
import pygame as pg
import os
from os.path import join as path_join
from sys import stderr
from typing import List, Tuple, Union
from dataclasses import make_dataclass
from game.pacman import Game, Direction
from game.controllers import *
from time import perf_counter

# WINDOW_POSITION = (500, 120)

# os.environ["SDL_VIDEO_WINDOW_POS"] = (
#     str(WINDOW_POSITION[0]) + "," + str(WINDOW_POSITION[1])
# )

RES = path_join(os.path.dirname(__file__), "resources")
IMAGES_DIR = path_join(RES, "images")


def convert_image(name: str) -> pg.Surface:
    return pg.image.load(path_join(IMAGES_DIR, name)).convert_alpha()


def load_images():
    # need to have this pg.Surface to convert images
    pg.display.set_mode((1, 1), flags=pg.HIDDEN)
    mazes = ["maze-a.png", "maze-b.png", "maze-c.png", "maze-d.png"]
    pis = [
        [
            "mspacman-up-normal.png",
            "mspacman-up-open.png",
            "mspacman-up-closed.png",
        ],
        [
            "mspacman-right-normal.png",
            "mspacman-right-open.png",
            "mspacman-right-closed.png",
        ],
        [
            "mspacman-down-normal.png",
            "mspacman-down-open.png",
            "mspacman-down-closed.png",
        ],
        [
            "mspacman-left-normal.png",
            "mspacman-left-open.png",
            "mspacman-left-closed.png",
        ],
    ]

    gis = [
        [
            ["blinky-up-1.png", "blinky-up-2.png"],
            ["blinky-right-1.png", "blinky-right-2.png"],
            ["blinky-down-1.png", "blinky-down-2.png"],
            ["blinky-left-1.png", "blinky-left-2.png"],
        ],
        [
            ["pinky-up-1.png", "pinky-up-2.png"],
            ["pinky-right-1.png", "pinky-right-2.png"],
            ["pinky-down-1.png", "pinky-down-2.png"],
            ["pinky-left-1.png", "pinky-left-2.png"],
        ],
        [
            ["inky-up-1.png", "inky-up-2.png"],
            ["inky-right-1.png", "inky-right-2.png"],
            ["inky-down-1.png", "inky-down-2.png"],
            ["inky-left-1.png", "inky-left-2.png"],
        ],
        [
            ["sue-up-1.png", "sue-up-2.png"],
            ["sue-right-1.png", "sue-right-2.png"],
            ["sue-down-1.png", "sue-down-2.png"],
            ["sue-left-1.png", "sue-left-2.png"],
        ],
        [["edible-ghost-1.png", "edible-ghost-2.png"]],
        [["edible-ghost-blink-1.png", "edible-ghost-blink-2.png"]],
    ]

    maze_imgs = [convert_image(im) for im in mazes]
    pac_imgs = [[convert_image(im) for im in dir_] for dir_ in pis]
    ghost_imgs = [
        [[convert_image(im) for im in dir_] for dir_ in ghost] for ghost in gis
    ]
    fruits = convert_image("fruits.png")
    pg.display.quit()
    return maze_imgs, pac_imgs, ghost_imgs, fruits


class PacView:
    MAG = 2
    FPS = 25
    MAX_FPS = 100
    MIN_FPS = 1
    TOP_BORDER = 20

    FRUIT_SIZE = 16
    bounceY = [0, 1, 0, 0, -1, -1, -1, -1]

    is_visible: bool = False

    def __init__(self, game: Game, scale: float = 1):
        PacView.is_visible = True
        self.game: Game = game
        self.scale: int = 2 * scale
        self.fps = PacView.FPS
        self.width: int = game._maze.width * PacView.MAG
        self.height: int = (
            PacView.TOP_BORDER + game._maze.height * PacView.MAG + 20
        )
        self.mazes, self.pacs, self.ghosts, self.fruits = load_images()

        self.pac_man_dir: int = 0
        pg.font.init()
        self.font = pg.font.Font(path_join(RES, "verdana.ttf"), 11, bold=True)
        self.small_font = pg.font.Font(
            path_join(RES, "verdana.ttf"), 8, bold=True
        )

        self.surf: pg.Surface = None
        self.ss: pg.Surface = None

    def new_display(self) -> None:
        pg.init()
        pg.display.set_caption("Ms. PacMan")
        self.screen = pg.display.set_mode(
            (self.width * self.scale, self.height * self.scale),
            flags=pg.RESIZABLE,
        )

    def new_view(self):
        MAG = PacView.MAG
        game = self.game

        if self.surf is None:
            self.surf = pg.Surface((self.width, self.height))
            # sub surface for not drawing into headder
            self.ss = self.surf.subsurface(
                0,
                PacView.TOP_BORDER,
                self.width,
                self.height - PacView.TOP_BORDER,
            )

        ss = self.ss

        self.surf.fill(pg.Color("black"))

        # DRAW MAZE
        ss.blit(self.mazes[game.current_maze], (2, 6))

        # DRAW DEBUG INFO
        self._draw_debug_info(ss)

        # DRAW PILLS
        for pill, node in enumerate(game.get_node_indices_with_pills()):
            if game.check_pill(pill):
                x, y = game.get_xy(node)
                pg.draw.ellipse(
                    ss, pg.Color("white"), (x * MAG + 4, y * MAG + 8, 3, 3)
                )

        # DRAW POWER PILLS
        for pill, node in enumerate(game.get_node_indices_with_power_pills()):
            if game.check_power_pill(pill):
                x, y = game.get_xy(node)
                pg.draw.ellipse(
                    ss, pg.Color("white"), (x * MAG + 1, y * MAG + 5, 8, 8)
                )

        # DRAW FRUIT
        f = game.fruit_loc
        fr_size = PacView.FRUIT_SIZE
        if f != -1:  # fruit exists
            x, y = game.get_xy(f)
            bounce = PacView.bounceY[game.level_ticks % 8]
            f_type = game.get_fruit_type()
            ss.blit(
                self.fruits,
                (x * MAG, y * MAG + 2 + bounce),
                (f_type * fr_size, 0, fr_size, fr_size),
            )

        if game.ate_fruit_time > 0:  # recently eaten fruit - draw score
            x, y = game.get_xy(game.ate_fruit_loc)
            f_type = game.ate_fruit_type
            ss.blit(
                self.fruits,
                (x * MAG, y * MAG + 2),
                (f_type * fr_size, fr_size, fr_size, fr_size),
            )

        # DRAW PAC-MAN
        if 0 <= game.pac_dir < 4:
            self.pac_man_dir = game.pac_dir
        if game.eating_time == 0:  # currently not eating a ghost
            x, y = game.get_xy(game.pac_loc)
            ss.blit(
                self.pacs[self.pac_man_dir][(game.total_ticks % 6) // 2],
                (x * MAG - 1, y * MAG + 3),
            )

        # DRAW GHOSTS
        for g in range(game.NUM_GHOSTS):
            if g == game.get_eating_ghost():
                continue

            if game.is_in_lair(g):
                x, y = game.lair_x[g], game.lair_y[g]
            else:
                x, y = game.get_xy(game._ghost_locs[g])

            pulse = (game.total_ticks % 6) // 3
            if game.get_edible_time(g) > 0:
                im_index = (
                    5
                    if game.get_edible_time(g) < Game.EDIBLE_ALERT
                    and pulse == 0
                    else 4
                )
                dir = 0
            else:
                im_index = g
                dir = game._ghost_dirs[g]
            ss.blit(
                self.ghosts[im_index][dir][pulse], (x * MAG - 1, y * MAG + 3)
            )

        g = game.get_eating_ghost()
        if g >= 0:
            x, y = game.get_xy(game._ghost_locs[g])
            ss.blit(
                self.small_font.render(
                    str(game.eating_score), False, pg.Color("turquoise3")
                ),
                (x * MAG - 2, y * MAG + 13),
            )

        # DRAW LIVES
        for i in range(game.lives_remaining):
            ss.blit(self.pacs[Direction.RIGHT][0], (10 + 15 * i, 257))

        s = self.surf

        # DRAW GAME INFO
        s.blit(self.font.render("SCORE", False, pg.Color("white")), (95, 0))
        s.blit(
            self.font.render(
                "{:5d}".format(game.score), False, pg.Color("white")
            ),
            (95, 11),
        )

        level = game.current_level
        if level > 7:
            s.blit(self.font.render("LEVEL", False, pg.Color("white")), (7, 0))
            s.blit(
                self.font.render(
                    "{:5d}".format(level), False, pg.Color("white")
                ),
                (7, 11),
            )

        for i in range(min(level, 7)):
            ss.blit(
                self.fruits,
                (203 - 18 * i, 256),
                (i * fr_size, 0, fr_size, fr_size),
            )

        # DRAW GAME-OVER
        if game.game_over:
            ss.blit(
                self.font.render("GAME OVER", False, pg.Color("white")),
                (82, 140),
            )

        pg.transform.smoothscale(self.surf, self.screen.get_size(), self.screen)
        pg.display.update()

    def game_loop(
        self,
        pac_controller: PacManControllerBase,
        ghosts_controller: GhostController,
        time_limit: Union[float, None] = None,
    ) -> None:
        game: Game = self.game
        self.new_display()
        self.new_view()

        no_action = PacManAction()

        # START THE GAME
        clock = pg.time.Clock()
        while not game.game_over:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        return
                    if event.key in VALID_KEYS:
                        pac_controller.press_key(event.key)
                    elif event.key == pg.K_f:
                        if self.fps < PacView.MAX_FPS:
                            self.fps += 10
                    elif event.key == pg.K_s:
                        if self.fps > PacView.MIN_FPS:
                            self.fps -= 1
                    elif event.key == pg.K_d:
                        self.fps = PacView.FPS

            start = perf_counter()
            pac_controller.tick(game)
            tick_time = perf_counter() - start

            ghosts_controller.tick(game)

            if (
                not pac_controller.hijacked
                and time_limit
                and tick_time > time_limit
            ):
                pac_action: PacManAction = no_action
                no_action.reset()
                print(
                    f"slow tick {game.total_ticks} - {(tick_time * 1000):.1f} ms.",
                    file=stderr,
                )
            else:
                pac_action: PacManAction = pac_controller.get_action()
            ghosts_actions: GhostsActions = ghosts_controller.get_actions()

            # PAUSED?
            advance = True
            if pac_action.pause_simulation or ghosts_actions.pause_simulation:
                if not pac_action.next_frame and not ghosts_actions.next_frame:
                    advance = False
                pac_action.next_frame = False
                ghosts_actions.next_frame = False

            if advance:
                game.advance_game(
                    pac_action.direction,
                    [ga.direction for ga in ghosts_actions.actions],
                )

            clock.tick(self.fps)
            self.new_view()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN:
                    pg.quit()
                    return
            clock.tick(PacView.FPS)

    # =========================
    # VISUAL AIDS FOR DEBUGGING
    # =========================

    # For debugging/illustration only: draw colors in the maze
    # to check whether controller is working correctly or not,
    # can draw squares and lines (see NearestPillPacManVS for demonstration)
    DebugPointer = make_dataclass("DebugPointer", ["rect", "color"])
    DebugLine = make_dataclass("DebugLine", ["start", "end", "color"])
    DebugText = make_dataclass("DebugText", ["pos", "color", "text"])

    map_xy_for_lines = lambda xy: (
        xy[0] * PacView.MAG + 5,
        xy[1] * PacView.MAG + 10,
    )

    map_xy_for_text = lambda xy: (
        xy[0] * PacView.MAG + 6,
        xy[1] * PacView.MAG + 6,
    )

    map_xy_for_points = lambda xy: pg.Rect(
        xy[0] * PacView.MAG, xy[1] * PacView.MAG + 4.5, 10, 10
    )

    debug_pointers: List[DebugPointer] = []
    debug_lines: List[DebugLine] = []
    debug_texts: List[DebugText] = []

    @classmethod
    def add_points(
        cls, game: Game, color: str, node_indices: List[int]
    ) -> None:
        """
        Highlight certain nodes.

        Must be called every frame, pointers are deleted after they are drawn.
        """
        if cls.is_visible:
            cls.debug_pointers.extend(
                (
                    cls.DebugPointer(
                        rect,
                        pg.Color(color),
                    )
                    for rect in map(
                        cls.map_xy_for_points, map(game.get_xy, node_indices)
                    )
                )
            )

    @classmethod
    def add_lines(
        cls,
        game: Game,
        color: str,
        from_node_indices: List[int],
        to_node_indices: List[int],
    ) -> None:
        """
        Add a set of lines to be drawn.

        From and To indices length must be equal.
        Must be called every frame, pointers are deleted after they are drawn.
        """
        assert len(from_node_indices) == len(to_node_indices)
        if cls.is_visible:
            cls.debug_lines.extend(
                (
                    cls.DebugLine(start, to, pg.Color(color))
                    for start, to in zip(
                        map(
                            cls.map_xy_for_lines,
                            map(game.get_xy, from_node_indices),
                        ),
                        map(
                            cls.map_xy_for_lines,
                            map(game.get_xy, to_node_indices),
                        ),
                    )
                )
            )

    @classmethod
    def add_lines_xy(
        cls,
        color: str,
        from_xy: List[Tuple[int, int]],
        to_xy: List[Tuple[int, int]],
    ) -> None:
        """
        Add a set of lines between (from_x, from_y) to (to_x, to_y) to be drawn.

        From and To length must be equal.
        Must be called every frame, pointers are deleted after they are drawn.
        """
        assert len(from_xy) == len(to_xy)
        if cls.is_visible:
            cls.debug_lines.extend(
                (
                    cls.DebugLine(start, end, pg.Color(color))
                    for start, end in zip(
                        map(cls.map_xy_for_lines, from_xy),
                        map(cls.map_xy_for_lines, to_xy),
                    )
                )
            )

    @classmethod
    def add_text(
        cls, game: Game, color: str, node_index: int, text: str
    ) -> None:
        """
        Add a text to be drawn.

        Must be called every frame, pointers are deleted after they are drawn.
        """
        if cls.is_visible:
            cls.debug_texts.append(
                cls.DebugText(
                    cls.map_xy_for_text(game.get_xy(node_index)),
                    pg.Color(color),
                    text,
                )
            )

    @classmethod
    def add_text_xy(cls, color: str, x: int, y: int, text: str) -> None:
        """
        Add a text to be drawn.

        Must be called every frame, pointers are deleted after they are drawn.
        """
        if cls.is_visible:
            cls.debug_texts.append(
                cls.DebugText(
                    cls.map_xy_for_text((x, y)), pg.Color(color), text
                )
            )

    def _draw_debug_info(self, s: pg.Surface) -> None:
        """Draw added debug entities and clear them."""
        for dp in self.debug_pointers:
            pg.draw.rect(s, dp.color, dp.rect)

        for dl in self.debug_lines:
            pg.draw.line(s, dl.color, dl.start, dl.end)

        for dt in self.debug_texts:
            s.blit(self.font.render(dt.text, False, dt.color), dt.pos)

        self.debug_pointers.clear()
        self.debug_lines.clear()
        self.debug_texts.clear()
