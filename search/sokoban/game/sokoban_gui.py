#!/usr/bin/env python3
from game.board import Board
from game.action import EDirection
from typing import Tuple
import pygame as pg
from os.path import dirname
from os.path import join as path_join

IMAGES_DIR = path_join(dirname(__file__), "images")

TILE_SIZE = 64


def load_tiles():
    # need to have this pg.Surface to convert images
    pg.display.set_mode((1, 1), flags=pg.HIDDEN)
    BOX_IN_PLACE = pg.image.load(path_join(IMAGES_DIR, "gcrate.png")).convert()
    BOX = pg.image.load(path_join(IMAGES_DIR, "gcrate-dark.png")).convert()
    PLACE = pg.image.load(path_join(IMAGES_DIR, "gend.png")).convert()
    GROUND = pg.image.load(path_join(IMAGES_DIR, "ground.png")).convert()
    EPLAYER = pg.image.load(path_join(IMAGES_DIR, "eplayer.png")).convert()
    PLAYER = pg.image.load(path_join(IMAGES_DIR, "gsokoban.png")).convert()
    WALL = pg.image.load(path_join(IMAGES_DIR, "wall.png")).convert()
    pg.display.quit()
    # in order of flag represention
    return [GROUND, PLACE, BOX, BOX_IN_PLACE, PLAYER, EPLAYER, None, None, WALL]


class SokobanGUI:
    """
    Provide GUI for Sokoban game.
    """

    TPS = 20

    def __init__(self) -> None:
        self.screen: pg.Surface = None
        self.width: int = -1
        self.height: int = -1
        self.down_scale: bool = False
        self.clock: pg.time.Clock = None
        self.tiles = load_tiles()

    def close(self) -> None:
        pg.quit()

    def new_board(self, board: Board) -> None:
        pg.init()
        pg.display.set_caption("Sokoban")
        self.width = board.width
        self.height = board.height
        if self.width > 15 or self.height > 10:
            self.down_scale = True
            ts = TILE_SIZE // 2
        else:
            self.down_scale = False
            ts = TILE_SIZE

        self.screen = pg.display.set_mode(
            (
                self.width * ts,
                self.height * ts,
            )
        )
        self.clock = pg.time.Clock()
        self._draw_board(board)
        pg.display.update()

    def _draw_board(self, board: Board) -> None:
        if self.down_scale:
            surf = pg.Surface((TILE_SIZE * self.width, TILE_SIZE * self.height))
        else:
            surf = self.screen
        sequence = (
            (x * TILE_SIZE, y * TILE_SIZE)
            for y in range(self.height)
            for x in range(self.width)
        )
        sequence = (
            (self.tiles[s], (x, y))
            for s, (x, y) in zip(board.int_sequence(), sequence)
        )
        surf.blits(sequence)
        if self.down_scale:
            pg.transform.scale(
                surf,
                self.screen.get_size(),
                self.screen,
            )

    def draw_and_wait(self, board: Board, wait: bool = True) -> bool:
        """
        Draw board and if wait - waits for event.
        Return False when closed.
        """
        self._draw_board(board)
        pg.display.update()
        if wait:
            return self.wait_next()
        return True

    def choose_direction(
        self, possible_reverse: bool
    ) -> Tuple[int, EDirection]:
        """
        Return flag
        and if flag is 1 also sokoban direction corresponding to event.

        Flags:
        -1: close
         0: reset
         1: direction
         2: go back
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return -1, None
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        return -1, None
                    if event.key == pg.K_UP:
                        return 1, EDirection.UP
                    elif event.key == pg.K_RIGHT:
                        return 1, EDirection.RIGHT
                    elif event.key == pg.K_DOWN:
                        return 1, EDirection.DOWN
                    elif event.key == pg.K_LEFT:
                        return 1, EDirection.LEFT
                    elif possible_reverse and event.key == pg.K_b:
                        return 2, None
                    elif event.key == pg.K_r:
                        return 0, None
            self.clock.tick(SokobanGUI.TPS)

    def wait_next(self) -> bool:
        """
        Wait for keydown/quit event and return False if closed.
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        return False
                    return True
            self.clock.tick(SokobanGUI.TPS)
