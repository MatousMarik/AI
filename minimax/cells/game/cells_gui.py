from game.cells import Transfer, Game
from game.agent import Agent

from math import sqrt
from collections import namedtuple
import pygame as pg
from typing import List, Tuple
from os import environ
from os.path import dirname
from os.path import join as path_join

RESOURCES = path_join(dirname(__file__), "resources")

WIDTH, HEIGHT = (1200, 750)
WINDOW_POSITION = WINDOW_POSITION = (100, 75)
FPS = 30
TRANSPARENT = 175
TRANSPARENT_SCORE = 130

ZERO_COORDS = pg.Vector2(0, 0)

environ["SDL_VIDEO_WINDOW_POS"] = (
    str(WINDOW_POSITION[0]) + "," + str(WINDOW_POSITION[1])
)
Colors = namedtuple(
    "Colors",
    [
        "background",
        "end_background",
        "transfer_background",
        "link",
        "border",
        "text",
        "selected",
        "player_colors",
        "colorkey",
    ],
)
PlayerColors = namedtuple(
    "PlayerColors",
    ["small", "medium", "big", "arrow", "arrow_text", "arrow_text_background"],
)
COLORS = Colors(
    pg.Color("aquamarine3"),
    pg.Color("white"),
    pg.Color("white"),
    pg.Color("red"),
    pg.Color("black"),
    pg.Color("black"),
    pg.Color("yellow"),
    [
        PlayerColors(
            pg.Color("gray75"),
            pg.Color("gray75"),
            pg.Color("gray75"),
            pg.Color(51, 204, 0),
            pg.Color("red"),
            pg.Color(102, 255, 51),
        ),
        PlayerColors(
            pg.Color(255, 202, 123),
            pg.Color(255, 184, 77),
            pg.Color(255, 153, 0),
            pg.Color(255, 179, 102),
            pg.Color("black"),
            pg.Color(255, 153, 51),
        ),
        PlayerColors(
            pg.Color(217, 179, 255),
            pg.Color(179, 102, 255),
            pg.Color(128, 0, 255),
            pg.Color(102, 153, 255),
            pg.Color("red"),
            pg.Color(77, 136, 255),
        ),
    ],
    pg.Color(1, 2, 3),
)

Arrow = namedtuple("Arrow", "text_rect whole_rect surface transfer")


class CellsGUI:
    RADIUS_STEP = 0.4
    END_SIZE = (200, 150)
    END_FONT_SIZE = 100
    SCORE_FONT_SIZE = 30

    FRAMES_PER_TICK = FPS // 3
    MIN_FPT = 3

    FRAMES_CHANGE_REPEAT = MIN_FPT - 1

    def __init__(self, scale: float = 1) -> None:
        self.scale: float = scale
        self.fpt: int = -1
        self.last_fpt: int = -1

        pg.init()
        self.clock = pg.time.Clock()
        pg.font.init()
        self.score_font = pg.font.Font(
            path_join(RESOURCES, "verdana.ttf"),
            CellsGUI.SCORE_FONT_SIZE,
        )
        self.end_font = pg.font.Font(
            path_join(RESOURCES, "verdana.ttf"), CellsGUI.END_FONT_SIZE
        )

    def init_cells(
        self,
        size: Tuple[int, int],
        positions: List[Tuple[int, int]],
        neighbors: List[List[int]],
    ) -> None:
        """Initialize background for a new game."""

        neighbors = [
            [n for n in neighs if n > ci] for ci, neighs in enumerate(neighbors)
        ]

        w, h = size

        self.step = round(
            min(WIDTH * self.scale // w, HEIGHT * self.scale // h)
        )
        self.width = w * self.step + 1
        self.height = h * self.step + 1

        self.col_offsets = CellsGUI.get_offsets(positions, w)

        self.margin = self.step // 2
        self.centers = [
            (x * self.step + self.margin, y * self.step + self.margin)
            for x, y in positions
        ]
        self.radius = int(self.step * CellsGUI.RADIUS_STEP)
        self.board: pg.Surface = CellsGUI.get_board(
            (self.width, self.height),
            neighbors,
            self.centers,
            self.radius + 1,
        )

        self.cell_font = pg.font.Font(
            path_join(RESOURCES, "verdana.ttf"), self.radius
        )
        self.cell_font_small = pg.font.Font(
            path_join(RESOURCES, "verdana.ttf"), self.radius * 3 // 4
        )

        self._set_new_display()

    @staticmethod
    def get_offsets(positions, width) -> List[int]:
        counts = [0] * width
        for x, _ in positions:
            counts[x] += 1
        counts = [0] + counts
        cum_sum = 0
        return [cum_sum := cum_sum + c for c in counts]

    @staticmethod
    def get_board(size, neighbors, positions, radius) -> pg.Surface:
        bg = pg.Surface(size)
        bg.fill(COLORS.background)
        for p, nei in zip(positions, neighbors):
            for n in nei:
                pg.draw.line(bg, COLORS.link, p, positions[n], 3)
        for p in positions:
            pg.draw.circle(bg, COLORS.border, p, radius)
        return bg

    def draw_arrow(
        self, surf: pg.Surface, start, end, value, color: int = 0
    ) -> Tuple[pg.Rect, pg.Rect]:
        width = self.radius
        start = pg.Vector2(*self.centers[start])
        end = pg.Vector2(*self.centers[end])
        vector = end - start
        ds = vector.copy()
        try:
            ds.scale_to_length(width + 1)
        except Exception as e:
            print(value)
            raise e

        start = start + ds
        vector -= ds * 2
        end = start + vector
        ds.scale_to_length(width)
        perp = vector.rotate(90)
        perp.scale_to_length(width / 2)

        points = (
            start - perp,
            start + perp,
            end + perp - ds,
            end + perp * 3 - ds,
            end,
            end - perp * 3 - ds,
            end - perp - ds,
        )
        colors = COLORS.player_colors[color]
        r = pg.draw.polygon(
            surf,
            colors.arrow,
            points,
        )
        text = self.cell_font.render(
            str(value), True, colors.arrow_text, colors.arrow_text_background
        )
        tr = text.get_rect()
        tr.center = start + vector / 2
        surf.blit(text, tr)
        return tr, r.union(tr)

    def draw_transfers(
        self,
        transfers: List[Transfer],
        owner: int,
    ) -> None:
        self.screen.blit(self.screen2, ZERO_COORDS)
        arrows = pg.Surface(
            (self.width, self.height),
        )
        arrows.fill(COLORS.colorkey)
        arrows.set_colorkey(COLORS.colorkey)
        arrows.set_alpha(TRANSPARENT)
        for source, target, mass in transfers:
            self.draw_arrow(arrows, source, target, mass, owner)
        self.screen.blit(arrows, ZERO_COORDS)
        pg.display.update()

    def _set_new_display(self) -> None:
        pg.display.set_caption("Cell Wars")
        self.screen: pg.Surface = pg.display.set_mode(
            (self.width, self.height),
            # pg.SCALED,
        )
        self.screen2: pg.Surface = None

    @staticmethod
    def draw_scores(
        screen: pg.Surface,
        font: pg.font.Font,
        total_masses: List[int],
        round: int,
    ) -> None:
        off = pg.Vector2(10, 10)
        for pi, tm in enumerate(total_masses[1:], start=1):
            t = font.render(
                str(tm),
                True,
                COLORS.player_colors[pi].big,
                COLORS.end_background,
            )
            t.set_alpha(TRANSPARENT_SCORE)
            screen.blit(t, off)
            r = t.get_rect()
            off += (0, r.height + 10)
        t = font.render(
            str(round),
            True,
            COLORS.text,
            COLORS.end_background,
        )
        t.set_alpha(TRANSPARENT_SCORE)
        screen.blit(t, off)

    def draw_cells(
        self,
        owners: List[int],
        masses: List[int],
        sizes: List[int],
        total_masses: List[int],
        round: int,
    ) -> None:
        """Draws actual game state on prepared background."""
        self.masses = masses
        self.screen.blit(self.board, ZERO_COORDS)
        for position, owner, mass, size_i in zip(
            self.centers, owners, masses, sizes
        ):
            CellsGUI.draw_cell(
                self.screen,
                position,
                mass,
                COLORS.player_colors[owner][size_i],
                self.radius,
                self.cell_font if mass < 1000 else self.cell_font_small,
            )

        CellsGUI.draw_scores(self.screen, self.score_font, total_masses, round)

        pg.display.update()
        self.screen2 = self.screen.copy()

    @staticmethod
    def draw_cell(screen, position, mass, color, r, font) -> None:
        pg.draw.circle(screen, color, position, r)
        text = font.render(str(mass), True, COLORS.text)
        rect = text.get_rect()
        rect.center = position
        screen.blit(text, rect)

    def wait_next(self, *, auto_wait: bool = True) -> bool:
        """
        Wait for ENTER/SPACE/MOUSECLICK to continue ESC/QUIT to exit, or for +-FS for continual animation.
        Return bool whether not closed
        """
        last_rep = 0
        counter = 0
        while True:
            if auto_wait and self.fpt > 0 and counter >= self.fpt:
                return True
            if (
                self.fpt == -1
                or counter - last_rep >= CellsGUI.FRAMES_CHANGE_REPEAT
            ):
                keys = pg.key.get_pressed()
                if (
                    keys[pg.K_KP_PLUS]
                    or keys[pg.K_KP_MINUS]
                    or keys[pg.K_s]
                    or keys[pg.K_f]
                ):
                    # change fpt
                    if self.fpt == -1:
                        counter = 0
                        last_rep = counter
                        self.fpt = (
                            CellsGUI.FRAMES_PER_TICK
                            if self.last_fpt < 0
                            else self.last_fpt
                        )
                    elif keys[pg.K_KP_PLUS] or keys[pg.K_f]:
                        if self.fpt > CellsGUI.MIN_FPT:
                            self.fpt -= 1
                    elif keys[pg.K_KP_MINUS] or keys[pg.K_s]:
                        self.fpt += 1
                    last_rep = counter

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return False
                    if (
                        event.key == pg.K_RETURN
                        or event.key == pg.K_SPACE
                        or event.key == pg.K_KP_ENTER
                    ):
                        return True
                    if event.key == pg.K_p:
                        if self.fpt < 0 and self.last_fpt > 0:
                            self.fpt = self.last_fpt
                        else:
                            self.last_fpt = self.fpt
                            self.fpt = -1
                elif event.type == pg.MOUSEBUTTONDOWN:
                    return True
            counter += 1
            self.clock.tick(FPS)

    def draw_end_and_wait(self, winner: int) -> bool:
        if winner == 0:
            text = "DRAW"
        else:
            text = "PLAYER {} WIN".format(winner)
        text = self.end_font.render(
            text, True, COLORS.text, COLORS.end_background
        )
        r = text.get_rect()
        r.center = self.width // 2, self.height // 2
        self.screen.blit(text, r)
        pg.display.update()
        return self.wait_next(auto_wait=False)


class CellsGUIAgent(CellsGUI, Agent):
    TRANSFER_SIZE = (250, 150)
    TRANSFER_FONT_SIZE = 20
    TRANSFER_MAX_LEN = 4

    def __init__(self, scale: float = 1) -> None:
        super().__init__(scale)
        self.arrows: List[Arrow] = None

        pg.font.init()
        self.transfer_font = pg.font.Font(
            path_join(RESOURCES, "verdana.ttf"),
            round(CellsGUIAgent.TRANSFER_FONT_SIZE * self.scale),
        )
        self.transfer_base = self.init_transfer()

        self.transfer_body = self.transfer_font.render(
            "Type value and ENTER",
            True,
            COLORS.text,
            COLORS.transfer_background,
        )

    def init_transfer(self) -> pg.Surface:
        s = pg.Surface(
            (
                int(CellsGUIAgent.TRANSFER_SIZE[0] * self.scale),
                int(CellsGUIAgent.TRANSFER_SIZE[1] * self.scale),
            )
        )
        s.fill(COLORS.transfer_background)
        headder = self.transfer_font.render(
            "Mass to send:", True, COLORS.text, COLORS.transfer_background
        )
        r = headder.get_rect()
        r.center = s.get_rect().center
        r.y = CellsGUIAgent.TRANSFER_SIZE[1] / 5
        s.blit(headder, r)
        return s

    def init_cells(
        self,
        size: Tuple[int, int],
        positions: List[Tuple[int, int]],
        neighbors: List[List[int]],
    ) -> None:
        super().init_cells(size, positions, neighbors)
        self.arrows: List[Arrow] = []

    def clicked_cell_index(self, pos) -> int:
        r = self.radius + 1
        x, y = pos
        xm = x - self.margin
        col = xm // self.step
        off = xm - col * self.step
        if off > r:
            if off < self.step - r:
                # in between
                return -1
            else:
                col += 1

        for i, (cx, cy) in enumerate(
            self.centers[self.col_offsets[col] : self.col_offsets[col + 1]]
        ):
            if cy + r < y:
                # too low, skip
                continue
            if cy - r > y:
                # too high, end
                break

            # fine position, check
            if sqrt((x - cx) ** 2 + (y - cy) ** 2) <= r:
                return self.col_offsets[col] + i
        return -1

    def clicked_arrow_index(self, pos) -> int:
        for i, a in enumerate(self.arrows):
            if a.text_rect.collidepoint(pos):
                return i
        return -1

    @staticmethod
    def process_transfer_key(key, value) -> bool:
        """Return transfer ending - bool/None, with creation of the new Transfer - bool."""
        if key == pg.K_RETURN or key == pg.K_KP_ENTER:
            return True
        if key == pg.K_ESCAPE:
            return False

        if key == pg.K_BACKSPACE:
            if value:
                value.pop()
        elif key == pg.K_0 or key == pg.K_KP0:
            value.append("0")
        elif key == pg.K_1 or key == pg.K_KP1:
            value.append("1")
        elif key == pg.K_2 or key == pg.K_KP2:
            value.append("2")
        elif key == pg.K_3 or key == pg.K_KP3:
            value.append("3")
        elif key == pg.K_4 or key == pg.K_KP4:
            value.append("4")
        elif key == pg.K_5 or key == pg.K_KP5:
            value.append("5")
        elif key == pg.K_6 or key == pg.K_KP6:
            value.append("6")
        elif key == pg.K_7 or key == pg.K_KP7:
            value.append("7")
        elif key == pg.K_8 or key == pg.K_KP8:
            value.append("8")
        elif key == pg.K_9 or key == pg.K_KP9:
            value.append("9")
        return None

    def add_arrow(self, start, end, value) -> None:
        transfer = Transfer(start, end, value)
        arrow = pg.Surface((self.width, self.height))
        arrow.set_colorkey(COLORS.colorkey)
        arrow.fill(COLORS.colorkey)
        tr, r = self.draw_arrow(arrow, start, end, value)
        self.arrows.append(Arrow(tr, r, arrow.subsurface(r), transfer))
        arrow.set_alpha(TRANSPARENT)

    def draw_neutral_arrows(self):
        arrows = pg.Surface((self.width, self.height))
        arrows.set_colorkey(COLORS.colorkey)
        arrows.fill(COLORS.colorkey)
        for _, r, s, _ in self.arrows:
            arrows.blit(s, r)
        arrows.set_alpha(TRANSPARENT)
        self.screen.blit(arrows, ZERO_COORDS)

    def draw_transfer(self, value: str = None) -> None:
        s = self.transfer_base.copy()
        if value:
            t = self.transfer_font.render(
                str(value), True, COLORS.text, COLORS.transfer_background
            )
        else:
            t = self.transfer_body

        r = t.get_rect()
        r.center = s.get_rect().center
        r.y = CellsGUIAgent.TRANSFER_SIZE[1] / 5 * 3
        s.blit(t, r)
        r = s.get_rect()
        r.center = self.screen.get_rect().center
        self.screen.blit(s, r)

    def get_move(self, _: Game) -> List[Transfer]:
        clock = self.clock
        scr2 = self.screen2

        open_transfer = False
        selected = [-1, -1]
        value = []
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                if event.type == pg.KEYDOWN:
                    key = event.key
                    if open_transfer:
                        res = CellsGUIAgent.process_transfer_key(key, value)
                        if res is None:
                            self.draw_transfer(
                                "".join(
                                    value[-CellsGUIAgent.TRANSFER_MAX_LEN :]
                                )
                            )
                            continue

                        open_transfer = False
                        if res:
                            val = int(
                                "".join(
                                    value[-CellsGUIAgent.TRANSFER_MAX_LEN :]
                                )
                            )
                            self.add_arrow(*selected, val)

                        # else cancel transfer
                        value.clear()
                        selected[0], selected[1] = -1, -1
                    else:
                        if (
                            key == pg.K_RETURN or key == pg.K_KP_ENTER
                        ) and selected[0] == -1:
                            running = False
                        if key == pg.K_ESCAPE:
                            selected[0] = -1
                elif not open_transfer and event.type == pg.MOUSEBUTTONDOWN:
                    pos = event.pos
                    button = event.button

                    if button != 1 and button != 3:
                        continue  # left or right only

                    i = self.clicked_arrow_index(pos)
                    if i != -1:
                        t = self.arrows.pop(i).transfer
                        if button == 1:  # left - edit
                            open_transfer = True
                            selected[0], selected[1] = t.source, t.target
                            value = list(str(t.mass))
                            self.draw_transfer(str(t.mass))
                        # else right - remove
                        continue

                    i = self.clicked_cell_index(pos)
                    if i != -1:
                        if i == selected[0]:
                            selected[0] = -1
                        else:
                            if button == 1 and selected[0] != -1:
                                # select second (left click not selected)
                                selected[1] = i
                                open_transfer = True
                                self.draw_transfer()
                            else:
                                # select first or reselect first (right click other than selected)
                                selected[0] = i

            if not open_transfer:
                self.screen.blit(scr2, ZERO_COORDS)
                si = selected[0]
                if si != -1:
                    CellsGUI.draw_cell(
                        self.screen,
                        self.centers[si],
                        self.masses[si],
                        COLORS.selected,
                        self.radius,
                        self.cell_font,
                    )
                self.draw_neutral_arrows()
            pg.display.update()
            clock.tick(FPS)

        m = [a.transfer for a in self.arrows]
        self.arrows = []
        return m
