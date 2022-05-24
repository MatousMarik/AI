from connect_four.connect_four import ConnectFour
from minimax_templates import GameUI, Strategy
import pygame as pg
from typing import Optional

WHITE = pg.Color(255, 255, 255)
BLUE = pg.Color(0, 0, 222)
GREEN = pg.Color(0, 255, 0)
YELLOW = pg.Color(204, 204, 0)
RED = pg.Color(222, 0, 0)
TURQUOISE = pg.Color(0, 255, 255)

TILE_SIZE = 50
RADIUS = 20
LINE_WIDTH = 3


class ConnectFourGUI(GameUI):
    """
    Provides UI for Connect_Four game.
    """

    def __init__(
        self,
        strategy1: Strategy,
        strategy2: Optional[Strategy] = None,
        seed: int = 0,
    ):
        assert strategy1 is not None
        self.seed: int = seed
        self.game: ConnectFour = ConnectFour(seed)
        self.s1: int = 1
        self.strategy1: Strategy = strategy1
        self.strategy2: Optional[Strategy] = strategy2
        self.player_in_game: bool = strategy2 is None

        self.screen: pg.Surface = None

        self.to_unmark = []  # (x, y, color)

    def _move(self, strategy):
        result, move = self.game.move(strategy.action(self.game))
        if not result:
            raise ValueError("Invalid move.")
        return move

    def _draw_circle(self, x, y, color, fill=True):
        pg.draw.circle(
            self.screen,
            color,
            ((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE),
            RADIUS,
            0 if fill else LINE_WIDTH,
        )

    def _draw_move(self, x, y, p, win, mark=True, unmark=False):
        if unmark:
            for um in self.to_unmark:
                self._draw_circle(*um)
            self.to_unmark = []

        self._draw_circle(x, y, YELLOW if p == 1 else RED)

        if win is not None:
            x0, y0, dx, dy = win
            for i in range(4):
                self._draw_circle(x0 + i * dx, y0 + i * dy, GREEN, False)
        elif mark:
            self._draw_circle(x, y, TURQUOISE, False)
            self.to_unmark.append((x, y, YELLOW if p == 1 else RED))
        pg.display.update()

    def _init_pg(self, init_moves):
        pg.init()
        pg.display.set_caption("Connect Four")
        self.screen = pg.display.set_mode(
            (self.game.WIDTH * TILE_SIZE, self.game.HEIGHT * TILE_SIZE)
        )
        self._draw_empty(init_moves)

    def _draw_empty(self, init_moves):
        self.screen.fill(BLUE)
        for x in range(self.game.WIDTH):
            for y in range(self.game.HEIGHT):
                self._draw_circle(x, y, WHITE)
        for i, (x, y) in enumerate(init_moves):
            self._draw_circle(x, y, RED if i % 2 else YELLOW)
        pg.display.update()

    def _reset(self):
        self.seed += 1
        self.game = ConnectFour(self.seed)
        if self.player_in_game:
            self.s1 = 3 - self.s1
        self._draw_empty(self.game.init_moves)

    def play_loop(self):
        self._init_pg(self.game.init_moves)
        clock = pg.time.Clock()
        while True:
            # strategy vs player on the move - don't wait
            if (
                self.player_in_game
                and self.game.winner == -1
                and self.game.turn == self.s1
            ):
                m = self._move(self.strategy1)
                self._draw_move(*m, p=self.s1, win=self.game.win)
                continue

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # waited for next game
                    if self.game.winner != -1:
                        self._reset()
                        break

                    if self.player_in_game:
                        if self.game.turn == self.s1:
                            break

                        # get player move
                        x, _ = event.pos
                        x //= TILE_SIZE

                        result, move = self.game.move(x)
                        if not result:
                            # invalid player move
                            continue
                        self._draw_move(
                            *move,
                            p=3 - self.game.turn,
                            win=self.game.win,
                            mark=False,
                            unmark=True
                        )
                    else:
                        # strategy v strategy on the move - wait
                        move = self._move(
                            self.strategy1
                            if self.game.turn == self.s1
                            else self.strategy2
                        )
                        self._draw_move(
                            *move,
                            p=3 - self.game.turn,
                            win=self.game.win,
                            mark=True,
                            unmark=True
                        )
                        break
            clock.tick(20)
