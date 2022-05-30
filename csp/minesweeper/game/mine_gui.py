#!/usr/bin/env python3
from game.minesweeper import Board, Action, ActionFactory
import pygame as pg
from os.path import dirname
from os.path import join as path_join

IM_DIR = path_join(dirname(__file__), "images")

TILE_SIZE = 32


def load_tiles():
    return {
        "M": pg.image.load(path_join(IM_DIR, "mine.png")),
        0: pg.image.load(path_join(IM_DIR, "0.png")),
        1: pg.image.load(path_join(IM_DIR, "1.png")),
        2: pg.image.load(path_join(IM_DIR, "2.png")),
        3: pg.image.load(path_join(IM_DIR, "3.png")),
        4: pg.image.load(path_join(IM_DIR, "4.png")),
        5: pg.image.load(path_join(IM_DIR, "5.png")),
        6: pg.image.load(path_join(IM_DIR, "6.png")),
        7: pg.image.load(path_join(IM_DIR, "7.png")),
        8: pg.image.load(path_join(IM_DIR, "8.png")),
        "F": pg.image.load(path_join(IM_DIR, "flag.png")),
        ".": pg.image.load(path_join(IM_DIR, "hidden.png")),
        "S": pg.image.load(path_join(IM_DIR, "safe.png")),
    }


class MineGUI:
    """
    Provide UI for minesweeper game.
    """

    TPS = 20

    def __init__(self) -> None:
        self.screen = None
        self.width: int = -1
        self.height: int = -1
        self.clock: pg.time.Clock = None
        self.tiles = load_tiles()
        pass

    def new_board(self, board: Board) -> None:
        pg.init()
        pg.display.set_caption("Minesweeper")
        self.width = board.width
        self.height = board.height
        self.screen = pg.display.set_mode(
            (self.width * TILE_SIZE, self.height * TILE_SIZE), pg.SCALED
        )
        # draw all tiles as hidden
        hidden = self.tiles["."]
        sequence = (
            (hidden, (x * TILE_SIZE, y * TILE_SIZE))
            for x in range(self.width)
            for y in range(self.height)
        )
        self.screen.blits(sequence)
        self.screen.blit(
            self.tiles["S"],
            (
                board.last_safe_tile.x * TILE_SIZE,
                board.last_safe_tile.y * TILE_SIZE,
            ),
        )
        self.clock = pg.time.Clock()
        pg.display.update()

    def _draw_board(self, board: Board) -> None:
        sequence = (
            (self.tiles[t._di_()], (x * TILE_SIZE, y * TILE_SIZE))
            for (x, y), t in board.generator()
        )
        self.screen.blits(sequence)
        if board.last_safe_tile is not None:
            lst = board.last_safe_tile
            t = board.tile(lst.x, lst.y)
            if not t.visible and not t.flag:
                self.screen.blit(
                    self.tiles["S"], (lst.x * TILE_SIZE, lst.y * TILE_SIZE)
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

    def choose_action(self) -> Action:
        """
        Return minesweeper action corresponding to event.
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return None

                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    button = event.button

                    x = x // TILE_SIZE
                    y = y // TILE_SIZE

                    if button == 1:  # left
                        return ActionFactory.get_uncover_action(x, y)
                    if button == 3:  # right
                        return ActionFactory.get_flag_action(x, y)

                elif event.type == pg.KEYDOWN and event.key == pg.K_h:
                    return ActionFactory.get_advice_action()
            self.clock.tick(MineGUI.TPS)

    def wait_next(self) -> bool:
        """
        Wait for mouse/quit event and return False if closed.
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return False
                elif (
                    event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN
                ):
                    return True
            self.clock.tick(MineGUI.TPS)
