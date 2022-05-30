#!/usr/bin/env python3
from game.dino import *
from typing import Optional, Union, Tuple, Deque, List
from collections import deque
from dataclasses import dataclass
import pygame as pg
from os.path import dirname
from os.path import join as path_join

RESOURCES = path_join(dirname(__file__), "resources")


@dataclass
class DebugRect:
    rect: pg.Rect
    color: pg.Color


@dataclass
class DebugDinoRect:
    dxdy: pg.Vector2
    rect: pg.Rect
    color: pg.Color


@dataclass
class DebugLine:
    start: pg.Vector2
    end: pg.Vector2
    color: pg.Color


@dataclass
class DebugDinoLine:
    dxdy: pg.Vector2
    start: pg.Vector2
    vector: pg.Vector2
    color: pg.Color


@dataclass
class DebugText:
    xy: pg.Vector2
    text: str
    color: Union[str, Tuple[int, int, int]]


class DebugGame(Game):
    """
    Dino game with visual debugging possibilities.

    After adding shape to visualization you are getting reference to it
    for later removal.
    You can also use this reference to change the shape at any time.
    """

    def __init__(
        self, seed: Optional[int] = None, *, new_game: bool = True
    ) -> None:
        pg.font.init()
        self.debug_font = pg.font.Font(path_join(RESOURCES, "verdana.ttf"), 12)

        self.debug_rects: Deque[DebugRect] = deque()
        self.debug_dino_rects: List[DebugDinoRect] = []
        self.debug_lines: List[DebugLine] = []
        self.debug_moving_lines: Deque[DebugLine] = deque()
        self.debug_dino_lines: List[DebugDinoLine] = []
        self.debug_texts: List[DebugText] = []

        super().__init__(seed, new_game=new_game)

    def add_rect(
        self, rect: RectT, color: Union[str, Tuple[int, int, int]]
    ) -> DebugRect:
        """
        Visualize rectangle that will move with the ground
        and returns it for possible removal.
        """
        r = DebugRect(pg.Rect(*rect), pg.Color(color))
        self.debug_rects.append(r)
        return r

    def remove_rect(self, rect: DebugRect) -> None:
        self.debug_rects.remove(rect)

    def add_dino_rect(
        self,
        dino_dxdy: Coords,
        width: int,
        height: int,
        color: Union[str, Tuple[int, int, int]],
    ) -> DebugDinoRect:
        """
        Visualize rectangle that will move with dino
        and returns it for possible removal.
        """
        r = DebugDinoRect(
            pg.Vector2(dino_dxdy), pg.Rect(0, 0, width, height), pg.Color(color)
        )
        self.debug_dino_rects.append(r)
        return r

    def remove_dino_rect(self, rect: DebugDinoRect) -> None:
        self.debug_dino_rects.remove(rect)

    def add_line(
        self,
        start: Coords,
        end: Coords,
        color: Union[str, Tuple[int, int, int]],
    ) -> DebugLine:
        """
        Visualize line that will stay in fixed position
        and returns it for possible removal.
        """
        l = DebugLine(pg.Vector2(start), pg.Vector2(end), pg.Color(color))
        self.debug_lines.append(l)
        return l

    def remove_line(self, line: DebugLine) -> None:
        self.debug_lines.remove(line)

    def add_moving_line(
        self,
        start: Coords,
        end: Coords,
        color: Union[str, Tuple[int, int, int]],
    ) -> DebugLine:
        """
        Visualize line that will move with the ground
        and returns it for possible removal.
        """
        if start.x > end.x:
            start, end = end, start
        l = DebugLine(pg.Vector2(start), pg.Vector2(end), pg.Color(color))
        self.debug_moving_lines.append(l)
        return l

    def remove_moving_line(self, line: DebugLine) -> None:
        self.debug_moving_lines.remove(line)

    def add_dino_line(
        self,
        dino_dxdy: Coords,
        vector: Coords,
        color: Union[str, Tuple[int, int, int]],
    ) -> DebugDinoLine:
        """
        Visualize line that will move with the dino
        and returns it for possible removal.
        """
        l = DebugDinoLine(
            pg.Vector2(dino_dxdy),
            pg.Vector2(0, 0),
            pg.Vector2(vector),
            pg.Color(color),
        )
        self.debug_dino_lines.append(l)
        return l

    def remove_dino_line(self, line: DebugDinoLine) -> None:
        self.debug_dino_lines.remove(line)

    def add_text(
        self, xy: Coords, color: Union[str, Tuple[int, int, int]], text: str
    ) -> DebugText:
        """
        Visualize text that will stay in fixed position
        and returns it for possible removal.

        Note: text is rerendered each frame, so you can
              just change returned_reference.text to change the value.
        """
        t = DebugText(pg.Vector2(xy), text, color)
        self.debug_texts.append(t)
        return t

    def remove_text(self, text: DebugText) -> None:
        self.debug_texts.remove(text)

    def tick(self, move: DinoMove):
        super().tick(move)

        dc = self.dino.coords
        speed = self.speed

        for _ in range(len(self.debug_rects)):
            r = self.debug_rects.popleft()
            r.rect.x -= speed
            if r.rect.right > 0:
                self.debug_rects.append(r)

        for r in self.debug_dino_rects:
            r.rect.topleft = r.dxdy + dc

        for _ in range(len(self.debug_moving_lines)):
            l = self.debug_moving_lines.popleft()
            l.start.x -= speed
            l.end.x -= speed
            if l.end.x > 0:
                self.debug_moving_lines.append(l)

        for l in self.debug_dino_lines:
            l.start.update(l.dxdy + dc)

    def new_game(self, seed: Optional[int] = None) -> None:
        super().new_game(seed)
        self.debug_rects = deque()
        self.debug_dino_rects.clear()
        self.debug_lines.clear()
        self.debug_moving_lines = deque()
        self.debug_dino_lines.clear()
        self.debug_texts.clear()
