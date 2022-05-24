#!/usr/bin/env python3
from tic_tac_toe.tic_tac_toe import TicTacToe
from minimax_templates import GameUI, Strategy
import pygame as pg
from typing import Optional, Tuple


WHITE = pg.Color("white")
BLACK = pg.Color("black")
WIN_COLOR = pg.Color(255, 255, 128)
LINE_WIDTH = 4
WIDTH = 300
HEIGHT = 300
FPS = 10


def get_center_coord(col, row):
    return ((col + 0.5) * WIDTH / 3, (row + 0.5) * HEIGHT / 3)


def draw_circle(screen, c, r):
    pg.draw.circle(screen, BLACK, get_center_coord(c, r), WIDTH / 7, LINE_WIDTH)


def draw_cross(screen, c, r):
    x, y = get_center_coord(c, r)
    pg.draw.line(
        screen,
        BLACK,
        (x - WIDTH / 8, y - HEIGHT / 8),
        (x + WIDTH / 8, y + HEIGHT / 8),
        LINE_WIDTH,
    )
    pg.draw.line(
        screen,
        BLACK,
        (x - WIDTH / 8, y + HEIGHT / 8),
        (x + WIDTH / 8, y - HEIGHT / 8),
        LINE_WIDTH,
    )


def draw_win(screen, x, y, dx, dy, circle):
    for i in range(3):
        pg.draw.rect(
            screen,
            WIN_COLOR,
            (
                (x + dx * i) * WIDTH / 3 + LINE_WIDTH / 2,
                (y + dy * i) * HEIGHT / 3 + LINE_WIDTH / 2,
                WIDTH / 3 - LINE_WIDTH,
                HEIGHT / 3 - LINE_WIDTH,
            ),
        )
        if circle:
            draw_circle(screen, x + dx * i, y + dy * i)
        else:
            draw_cross(screen, x + dx * i, y + dy * i)


class TicTacToeGUI(GameUI):
    """Basic UI for TicTacToe game with 1-2 strategies."""

    def __init__(
        self,
        strategy1: Strategy,
        strategy2: Optional[Strategy] = None,
        seed: int = 0,
    ):
        assert strategy1 is not None
        self.game: TicTacToe = TicTacToe()
        self.s1: int = 1
        self.strategy1: Strategy = strategy1
        self.strategy2: Optional[Strategy] = strategy2
        self.player_in_game: bool = strategy2 is None
        self.screen: pg.Surface = None

    def move(self, strategy) -> Tuple[int, int]:
        """Let strategy perform action and return the result."""
        a = strategy.action(self.game)
        if not self.game.move(a):
            raise ValueError("Invalid move.")
        return a // 3, a % 3

    def draw_move(self, x: int, y: int) -> None:
        if self.game.winner() > 0:
            draw_win(
                self.screen,
                self.game.win_x,
                self.game.win_y,
                self.game.win_dx,
                self.game.win_dy,
                self.game.winner() == 1,
            )
        elif self.game.player() == 1:
            draw_cross(self.screen, x, y)
        else:
            draw_circle(self.screen, x, y)
        pg.display.update()

    def init_pg(self) -> None:
        """Initialize self.screen."""
        pg.init()
        pg.display.set_caption("Tic Tac Toe")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.draw_empty()

    def draw_empty(self) -> None:
        self.screen.fill(WHITE)
        pg.draw.line(
            self.screen, BLACK, (WIDTH / 3, 0), (WIDTH / 3, HEIGHT), LINE_WIDTH
        )
        pg.draw.line(
            self.screen,
            BLACK,
            (WIDTH / 3 * 2, 0),
            (WIDTH / 3 * 2, HEIGHT),
            LINE_WIDTH,
        )
        pg.draw.line(
            self.screen, BLACK, (0, HEIGHT / 3), (WIDTH, HEIGHT / 3), LINE_WIDTH
        )
        pg.draw.line(
            self.screen,
            BLACK,
            (0, HEIGHT / 3 * 2),
            (WIDTH, HEIGHT / 3 * 2),
            LINE_WIDTH,
        )
        pg.display.update()

    def reset(self) -> None:
        self.game = TicTacToe()
        if self.player_in_game:
            self.s1 = 3 - self.s1
        self.draw_empty()

    def play_loop(self) -> None:
        self.init_pg()
        clock = pg.time.Clock()
        while True:
            # strategy vs player on the move - don't wait
            if (
                self.player_in_game
                and self.game.winner() == -1
                and self.game.player() == self.s1
            ):
                m = self.move(self.strategy1)
                self.draw_move(*m)
                continue

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # waited for new game
                    if self.game.winner() != -1:
                        self.reset()
                        break

                    if self.player_in_game:
                        if self.game.player() == self.s1:
                            break

                        # get player move
                        x, y = event.pos
                        col = x // (WIDTH / 3)
                        if col > 2:
                            col = None
                        row = y // (HEIGHT / 3)
                        if row > 2:
                            row = None
                        c, r = int(col), int(row)

                        if not self.game.move(c, r):
                            # invalid player move
                            continue
                        self.draw_move(c, r)
                    else:
                        # strategy v strategy on the move - wait
                        m = self.move(
                            self.strategy1
                            if self.game.player() == self.s1
                            else self.strategy2
                        )
                        self.draw_move(*m)
                        break
            clock.tick(20)
