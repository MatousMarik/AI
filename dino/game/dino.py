#!/usr/bin/env python3
from collections import namedtuple, deque
from enum import Enum
from typing import Optional, Tuple, Deque
from random import Random


WIDTH = 1100
HEIGHT = 600

Coords = namedtuple("Coords", "x y")
RectT = namedtuple("RectT", "x y width height")
# br for bottom right
RectT_br = namedtuple("RectT_br", "top left bottom right")


class DinoMove(Enum):
    """
    Possible dino moves.

    Tuple of movements up and right, where both can be True, None and False.
    None means no movement along axis.
    False means movement in the opposite direction.

    This representation prevents movement in the opposite directions
    at the same time.
    """

    NO_MOVE = (None, None)
    UP = (True, None)
    UP_RIGHT = (True, True)
    RIGHT = (None, True)
    DOWN_RIGHT = (False, True)
    DOWN = (False, None)
    DOWN_LEFT = (False, False)
    LEFT = (None, False)
    UP_LEFT = (True, False)

    def __init__(self, UP, RIGHT) -> None:
        self.UP: Optional[bool] = UP
        self.RIGHT: Optional[bool] = RIGHT


class DinoState(Enum):
    RUNNING = (1, 32, 48)
    JUMPING = (2, 32, 48)
    DUCKING = (3, 56, 13)

    def __init__(self, i, head_width, body_height):
        self.index = i
        self.head_width = head_width
        self.body_height = body_height


class ObstacleType(Enum):
    SMALL_CACTUS1 = (325, 40, 71)
    SMALL_CACTUS2 = (325, 68, 71)
    SMALL_CACTUS3 = (325, 105, 71)
    LARGE_CACTUS1 = (300, 48, 95)
    LARGE_CACTUS2 = (300, 99, 95)
    LARGE_CACTUS3 = (300, 102, 95)
    BIRD1 = (265, 92, 50)
    BIRD2 = (215, 92, 50)
    BIRD3 = (295, 92, 50)

    def __init__(self, y, width, height) -> None:
        self.y = y
        self.width = width
        self.height = height

    @classmethod
    def small_cactus(cls, index) -> "ObstacleType":
        if index <= 1:
            return cls.SMALL_CACTUS1
        elif index == 2:
            return cls.SMALL_CACTUS2
        elif index == 3:
            return cls.SMALL_CACTUS3
        else:
            raise RuntimeError("Invalid small cactus index.")

    @classmethod
    def large_cactus(cls, index) -> "ObstacleType":
        if index <= 1:
            return cls.LARGE_CACTUS1
        elif index == 2:
            return cls.LARGE_CACTUS2
        elif index == 3:
            return cls.LARGE_CACTUS3
        else:
            raise RuntimeError("Invalid large cactus index.")

    @classmethod
    def bird(cls, index) -> "ObstacleType":
        if index <= 1:
            return cls.BIRD1
        elif index == 2:
            return cls.BIRD2
        elif index == 3:
            return cls.BIRD3


class Rect:
    """Class for dino sprites collision boxes."""

    def __init__(self, x, y, width, height):
        self.x: float = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

    def move_x(self, dx: int) -> None:
        self.x += dx

    def is_gone(self) -> bool:
        return self.x <= -self.width

    @property
    def top(self) -> int:
        return self.y

    @property
    def left(self) -> int:
        return self.x

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def coords(self) -> Coords:
        return Coords(self.x, self.y)

    @property
    def tuple(self) -> RectT:
        return RectT(self.x, self.y, self.width, self.height)

    @property
    def tuple_br(self) -> RectT_br:
        """Top left bottom right."""
        return RectT_br(
            self.y, self.x, self.y + self.height, self.x + self.width
        )

    @staticmethod
    def rectT_to_br(rect: RectT) -> RectT_br:
        """Return RectT_br representation of RectT."""
        return RectT_br(
            rect.y, rect.x, rect.y + rect.height, rect.x + rect.width
        )

    @staticmethod
    def rectT_br_to_rectT(rect: RectT_br) -> RectT:
        """Return RectT representation of RectT_br"""
        return RectT(
            rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top
        )

    @staticmethod
    def collision(t1, l1, b1, r1, t2, l2, b2, r2) -> bool:
        """Whether two [top left bottom right] rectangles collide."""
        return t1 < b2 and l1 < r2 and b1 > t2 and r1 > l2


class Obstacle:
    def __init__(self, type: ObstacleType, speed: int = 0) -> None:
        self.type = type
        self.rect = Rect(WIDTH, type.y, type.width, type.height)
        self.speed = speed

    def tick(self, speed: float) -> bool:
        """Move obstacle and return whether it is gone."""
        self.rect.x -= self.speed + speed
        return self.rect.is_gone()


class Dino:
    """
    Sprite of dino.

    Dino collision area is represented by two rectangles - head and body.
    """

    MAX_HEIGHT = 80
    MAX_WIDTH = 101

    HEAD_X = 45
    HEAD_HEIGHT = 40

    BODY_Y = 32
    BODY_WIDTH = 50

    X = 80
    X_MAX = WIDTH * 2 // 3
    Y = 310
    Y_DUCK = 340

    # params for 30 FPS
    JUMP_VEL = 20
    FALL_VEL = -4
    JUMP_DECAY = 1

    def __init__(self) -> None:
        # AGENT MIGHT WANT TO ACCESS THESE:
        self.x: float = Dino.X
        self.y: int = Dino.Y

        # velocities
        self.jump_vel: float = Dino.JUMP_VEL
        self.move_vel: float = 0

        self.state: DinoState = DinoState.RUNNING

    def _fell(self) -> bool:
        """Dino fell to the ground."""
        # MAX_HEIGHT can be used because dino is surely standing
        # when this method is called
        return self.y + Dino.MAX_HEIGHT >= Game.GROUND_Y

    def tick(self, speed: float, action: DinoMove) -> None:
        """
        Move dino according to given movement.

        Set state and rectangle.

        Horizontal movement:
            Left/right movement causes acceleration along the x-axis.
            Once direction is changed acceleration is reset.
        Vertical movement:
            When running, dino can duck to avoid collision with flying bird
            by moving down or it can initialize jump by moving up.
            Once jump is initialized dino gets upwards velocity
            that continuously decrease until dino falls.
            During the jump down movement cause upward velocity
            to instantly decrease to negative values and decrease more quickly.
        """
        fall = False
        if action.UP is not None:
            if action.UP:
                self.state = DinoState.JUMPING
            else:  # DOWN
                if self.state == DinoState.JUMPING:
                    fall = True
                elif self.state != DinoState.DUCKING:
                    self.state = DinoState.DUCKING
                    self.y = Dino.Y_DUCK
        elif self.state != DinoState.JUMPING:
            # stop ducking
            self.state = DinoState.RUNNING
            self.y = Dino.Y

        self._move(action.RIGHT, speed)
        if self.state == DinoState.JUMPING:
            self._jump(fall)

    def _jump(self, fall: bool) -> None:
        # jump movement
        self.y -= self.jump_vel
        if fall:
            if self.jump_vel > 0:
                self.jump_vel = Dino.FALL_VEL
            else:
                self.jump_vel -= Dino.JUMP_DECAY * 2
        else:
            self.jump_vel -= Dino.JUMP_DECAY

        # stop jump
        if self._fell():
            self.state = DinoState.RUNNING
            self.y = Dino.Y
            self.jump_vel = Dino.JUMP_VEL

    def _move(self, right: Optional[bool], speed: float) -> None:
        if right is None:
            self.move_vel = -speed
        elif right:
            if self.move_vel < 0:
                self.move_vel = 1
            else:
                self.move_vel += 1
        else:
            if self.move_vel > 0:
                self.move_vel = -1
            else:
                self.move_vel -= 1

        if Dino.X < self.x + self.move_vel < Dino.X_MAX:
            self.x += self.move_vel

    def get_rects(self) -> Tuple[Rect, Rect]:
        """Return rectangles of dino's head and body."""
        return Rect(
            self.x + Dino.HEAD_X,
            self.y,
            self.state.head_width,
            Dino.HEAD_HEIGHT,
        ), Rect(
            self.x,
            self.y + Dino.BODY_Y,
            Dino.BODY_WIDTH,
            self.state.body_height,
        )

    def collision(self, rect: Rect) -> bool:
        """Checks top right dino corner, then body or head."""
        rect_br = rect.tuple_br
        # top right
        if self.x + Dino.MAX_WIDTH <= rect_br.left or self.y >= rect_br.bottom:
            return False

        return Rect.collision(*self.body_br, *rect_br) or Rect.collision(
            *self.head_br, *rect_br
        )

    @property
    def head(self) -> RectT:
        """RectT representation of dino's head area."""
        return RectT(
            self.x + Dino.HEAD_X,
            self.y,
            self.state.head_width,
            Dino.HEAD_HEIGHT,
        )

    @property
    def head_br(self) -> RectT_br:
        """RectT_br representation of dino's head area."""
        return RectT_br(
            self.y,
            self.x + Dino.HEAD_X,
            self.y + Dino.HEAD_HEIGHT,
            self.x + Dino.HEAD_X + self.state.head_width,
        )

    @property
    def body(self) -> RectT:
        """RectT representation of dino's body area."""
        return RectT(
            self.x,
            self.y + Dino.BODY_Y,
            Dino.BODY_WIDTH,
            self.state.body_height,
        )

    @property
    def body_br(self) -> RectT_br:
        """RectT representation of dino's body area."""
        return RectT_br(
            self.y + Dino.BODY_Y,
            self.x,
            self.y + Dino.BODY_Y + self.state.body_height,
            self.x + Dino.BODY_WIDTH,
        )

    @property
    def coords(self) -> Coords:
        return Coords(self.x, self.y)


class Game:
    """
    Represent state of the dino game.
    """

    WIDTH = WIDTH
    HEIGHT = HEIGHT

    SPAWN = 0.04
    SPAWN_INC = 0.001
    PREVIOUS_OBSTACLE = WIDTH - 300
    SPEED = 5
    INC_INTEVAL = 100
    SPEED_INC = 0.3
    GROUND_Y = 404

    def __init__(
        self, seed: Optional[int] = None, *, new_game: bool = True
    ) -> None:
        self.rnd: Random = Random(seed)

        if new_game:
            self.new_game()

    def new_game(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.rnd = Random(seed)

        # AGENT MIGHT WANT TO ACCESS THESE:
        self.dino = Dino()
        self.obstacles: Deque[Obstacle] = deque()  # ordered from youngest
        self.speed = Game.SPEED

        self.score: int = 0
        self.game_over: int = False
        self.spawn = Game.SPAWN
        self.previous_obstacle = Game.PREVIOUS_OBSTACLE

    def _add_obstacle(self) -> None:
        """
        If previous obstacle is far enough
        randomly add obstacle with respect to spawn.
        """
        if len(self.obstacles) == 0 or (
            self.obstacles[0].rect.x < self.previous_obstacle
            and self.rnd.random() < self.spawn
        ):
            r = self.rnd.randrange(0, 100)
            if r < 25:
                self.obstacles.appendleft(
                    Obstacle(ObstacleType.small_cactus(self.score % 4)),
                )
            elif r < 40:
                self.obstacles.appendleft(
                    Obstacle(ObstacleType.large_cactus(self.score % 4)),
                )
            elif r < 70:
                self.obstacles.appendleft(
                    Obstacle(
                        ObstacleType.bird(self.score % 4),
                        int(self.rnd.expovariate(self.speed // 2)),
                    ),
                )

    def _update_obstacles(self) -> None:
        for _ in range(len(self.obstacles)):
            ob = self.obstacles.pop()
            if not ob.tick(self.speed):
                # obstacle did not leave game field
                self.obstacles.appendleft(ob)
                if self.dino.collision(ob.rect):
                    self.game_over = True
                    return

    def tick(self, move: DinoMove):
        """
        Update dino, sprites, speed and score.

        Dino is moved according to provided move.
        """

        self._add_obstacle()

        self.dino.tick(self.speed, move)

        self._update_obstacles()

        self.score += 1
        if self.score % Game.INC_INTEVAL == 0:
            self.speed += Game.SPEED_INC
            self.previous_obstacle += 1
            self.spawn += Game.SPAWN_INC
