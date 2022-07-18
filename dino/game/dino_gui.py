#!/usr/bin/env python3
from game.dino import *
from game.debug_game import DebugGame
from game.agent import Agent
from typing import Optional, Union
import pygame as pg
from os import environ
from os.path import dirname
from os.path import join as path_join
from dataclasses import make_dataclass

# WINDOW_POSITION = (150, 120)

# environ["SDL_VIDEO_WINDOW_POS"] = (
#     str(WINDOW_POSITION[0]) + "," + str(WINDOW_POSITION[1])
# )

WHITE = pg.Color("white")
BLACK = pg.Color("black")

RESOURCES = path_join(dirname(__file__), "resources")


def convert_image(name: str) -> pg.Surface:
    return pg.image.load(path_join(RESOURCES, name)).convert_alpha()


Images = make_dataclass(
    "Images",
    [
        "track",
        "reset",
        "game_over",
        "start",
        "obstacles",
        "dead",
        "ducks",
        "jump",
        "runs",
        "start_text",
    ],
)


def load_images():
    # need to have this pg.Surface to convert images
    pg.display.set_mode((1, 1), flags=pg.HIDDEN)
    pg.font.init()
    font = pg.font.Font(path_join(RESOURCES, "FreeSansBold.ttf"), 30)
    birds = [convert_image("Bird{:d}.png".format(b)) for b in range(1, 3)]
    ret = Images(
        convert_image("Track.png"),
        convert_image("Reset.png"),
        convert_image("GameOver.png"),
        convert_image("DinoStart.png"),
        {
            ObstacleType.BIRD1: birds,
            ObstacleType.BIRD2: birds,
            ObstacleType.BIRD3: birds,
            ObstacleType.LARGE_CACTUS1: convert_image("LargeCactus1.png"),
            ObstacleType.LARGE_CACTUS2: convert_image("LargeCactus2.png"),
            ObstacleType.LARGE_CACTUS3: convert_image("LargeCactus3.png"),
            ObstacleType.SMALL_CACTUS1: convert_image("SmallCactus1.png"),
            ObstacleType.SMALL_CACTUS2: convert_image("SmallCactus2.png"),
            ObstacleType.SMALL_CACTUS3: convert_image("SmallCactus3.png"),
        },
        convert_image("DinoDead.png"),
        [convert_image("DinoDuck{:d}.png".format(d)) for d in range(1, 3)],
        convert_image("DinoJump.png"),
        [convert_image("DinoRun{:d}.png".format(r)) for r in range(1, 3)],
        font.render("Press any Key to Start", True, BLACK),
    )
    pg.display.quit()
    return ret


def keys_to_move(keys):
    up = None
    if keys[pg.K_UP]:
        up = True
    elif keys[pg.K_DOWN]:
        up = False
    right = None
    if keys[pg.K_RIGHT]:
        right = True
    elif keys[pg.K_LEFT]:
        right = False
    return DinoMove((up, right))


class Dino_GUI:
    FPS = 30
    SWAPS_PS = 3
    SIZE = (WIDTH, HEIGHT)

    DINO_X_OFFSET = -5
    BIRD1_Y_OFFSET = -15
    BIRD2_Y_OFFSET = -1

    TRACK_XY = (0, 380)

    IN_GAME_SCORE_CENTER = (1000, 40)
    SCORE_CENTER = (WIDTH // 2, HEIGHT // 2 + 50)
    TEXT_CENTER = (WIDTH // 2, HEIGHT // 2)
    PIC_POS = (WIDTH // 2 - 40, HEIGHT // 2 - 140)

    FLIP_INTERVAL = 8

    def __init__(
        self,
        agent: Union[Agent, None],
        game: Game,
        vis_rect: bool = False,
        *,
        debug=False
    ) -> None:
        self.game: Game = game
        self.agent: Optional[Agent] = agent
        self.vis_rect: bool = vis_rect
        self.debug: bool = debug

        self.images: Images = load_images()
        pg.font.init()
        self.font = pg.font.Font(path_join(RESOURCES, "FreeSansBold.ttf"), 20)
        self.screen: pg.Surface = self._new_display()

    def _new_display(self) -> pg.Surface:
        pg.init()
        pg.display.set_caption("Dino")
        return pg.display.set_mode(Dino_GUI.SIZE)

    def play(self) -> None:
        self._new_game(True)
        self._wait_loop()

    def _new_game(self, first: bool = False) -> None:
        self.screen.fill(WHITE)
        rect = self.images.start_text.get_rect()
        rect.center = Dino_GUI.TEXT_CENTER
        self.screen.blit(self.images.start_text, rect)
        self.screen.blit(self.images.runs[0], Dino_GUI.PIC_POS)
        if not first:
            score = self.font.render(
                "Your Score: {:d}".format(self.game.score),
                True,
                BLACK,
            )
            rect = score.get_rect()
            rect.center = Dino_GUI.SCORE_CENTER
            self.screen.blit(score, rect)
        self.game.new_game()
        pg.display.update()

    def _wait_loop(self) -> None:
        clock = pg.time.Clock()
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        return
                    if self._game_loop(clock):
                        pg.quit()
                        return
                    self._new_game()
                    pg.time.delay(200)
            clock.tick(Dino_GUI.FPS)

    def _game_loop(self, clock: pg.time.Clock) -> bool:
        """Return quit."""
        # load references for faster access
        scr = self.screen
        game = self.game
        dino = game.dino
        ims = self.images
        track_width: int = ims.track.get_width()
        track_x, track_y = Dino_GUI.TRACK_XY

        swap = Dino_GUI.FPS // Dino_GUI.SWAPS_PS

        t = 0
        ii = 0
        while not game.game_over:
            # swaps index for "moving" images
            # (dino moving legs and birds flapping wings)
            if swap == 0 or t % swap == 0:
                ii = 1 - ii

            for event in pg.event.get():
                if (
                    event.type == pg.QUIT
                    or event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE
                ):
                    pg.quit()
                    return True
            move = (
                self.agent.get_move(game)
                if self.agent
                else keys_to_move(pg.key.get_pressed())
            )
            game.tick(move)
            clock.tick(Dino_GUI.FPS)

            # DRAW GAME
            scr.fill(WHITE)

            # draw score
            text = self.font.render(
                "SCORE: {:d}".format(game.score), True, BLACK
            )
            rect = text.get_rect()
            rect.center = Dino_GUI.IN_GAME_SCORE_CENTER
            scr.blit(text, rect)

            # draw track, if track is ending, append it at the end
            if track_x + track_width < scr.get_width():
                # end of track
                if track_x + track_width <= 5:
                    # new cycle
                    track_x += track_width
                else:
                    # old + new cycle
                    scr.blit(ims.track, (track_x + track_width - 5, track_y))
            scr.blit(ims.track, (track_x, track_y))
            track_x -= game.speed

            # draw dino
            if dino.state == DinoState.RUNNING:
                dim = ims.runs[ii]
            elif dino.state == DinoState.DUCKING:
                dim = ims.ducks[ii]
            else:
                dim = ims.jump
            x, y = dino.coords
            scr.blit(dim, (x + Dino_GUI.DINO_X_OFFSET, y))

            if self.vis_rect:
                pg.draw.rect(scr, pg.Color("blue"), dino.head, 1)
                pg.draw.rect(scr, pg.Color("blue"), dino.body, 1)

            # draw obstacles
            for ob in game.obstacles:
                if (
                    ob.type == ObstacleType.BIRD1
                    or ob.type == ObstacleType.BIRD2
                    or ob.type == ObstacleType.BIRD3
                ):
                    x, y = ob.rect.coords
                    if ii == 1:
                        scr.blit(
                            ims.obstacles[ob.type][ii],
                            (x, y + Dino_GUI.BIRD1_Y_OFFSET),
                        )
                    else:
                        scr.blit(
                            ims.obstacles[ob.type][ii],
                            (x, y + Dino_GUI.BIRD2_Y_OFFSET),
                        )

                else:
                    scr.blit(
                        ims.obstacles[ob.type],
                        ob.rect.coords,
                    )
                if self.vis_rect:
                    pg.draw.rect(scr, pg.Color("red"), ob.rect.tuple, 1)

                if self.debug:
                    self.draw_debug_info(scr, game)

            pg.display.update()
            t += 1

        pg.time.delay(500)
        return False

    def draw_debug_info(self, s: pg.Surface, game: DebugGame) -> None:
        for r in game.debug_rects:
            pg.draw.rect(s, r.color, r.rect, 1)
        for r in game.debug_dino_rects:
            pg.draw.rect(s, r.color, r.rect, 1)
        for l in game.debug_lines:
            pg.draw.line(s, l.color, l.start, l.end)
        for l in game.debug_moving_lines:
            pg.draw.line(s, l.color, l.start, l.end)
        for l in game.debug_dino_lines:
            pg.draw.line(s, l.color, l.start, l.start + l.vector)
        for t in game.debug_texts:
            s.blit(game.debug_font.render(t.text, False, t.color), t.xy)
