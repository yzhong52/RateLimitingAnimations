from abc import ABC
from collections import defaultdict
from random import random, randint

from manim import *

import numpy as np

CLIENT1 = "Client 1"


def pos(x: float, y: float):
    return np.array([x, y, 0])


class Box(Square, ABC):
    def __init__(self, x: float, y: float, **kwargs):
        side_length = 1.0
        # Shrink the box a bit so that it won't overlap with nearby boxes
        super().__init__(
            side_length=side_length - 0.04,
            **kwargs
        )

        self.set_x(x + side_length / 2)
        # Move the box up a bit so that it won't overlap with the horizontal x-axis
        self.set_y(y + side_length / 2 + 0.02)


class RateLimiter:
    # Should be called once per second
    def tick(self, current_time: int):
        pass

    def check(self, client_id: str) -> bool:
        return False


class FixedWindow(RateLimiter):
    def __init__(self):
        self.window = 5
        self.limit = 5
        self.counter = defaultdict(int)

    def tick(self, current_time: int):
        if self.window == 1 or current_time % self.window == 0:
            # Reset counters
            self.counter = defaultdict(int)

    def check(self, client_id: str) -> bool:
        self.counter[client_id] += 1
        return self.counter[client_id] <= self.limit


class TokenBucketLimiter(RateLimiter):
    def __init__(self, clients: List[str]):
        super().__init__()
        self.window = 5
        self.limit = 5
        self.tokens = defaultdict(int)
        for client in clients:
            self.tokens[client] = 0
        self.last_time = -1

    def tick(self, current_time: int):
        if self.last_time == current_time:
            return
        self.last_time = current_time

        # Add one token per second
        for client_id in self.tokens:
            self.tokens[client_id] = min(self.limit, self.tokens[client_id] + 1)

    def check(self, client_id: str) -> bool:
        self.tokens[client_id] -= 1
        should_allow = self.tokens[client_id] >= 0
        self.tokens[client_id] = max(0, self.tokens[client_id])
        return should_allow


class RateLimitScene(MovingCameraScene):
    def get_rate_limiter(self) -> RateLimiter:
        pass

    def get_label(self) -> str:
        pass

    def get_counter_label(self) -> int:
        pass

    def construct(self):
        x_axis = Arrow(start=pos(-1, 0), end=pos(11, 0), stroke_width=4)
        for x in range(0, 11):
            line = Line(pos(x, -0.1), pos(x, 0.1))
            text = Text(f"{x}", font_size=24).next_to(line, DOWN)
            self.add(line, text)
        self.add(x_axis)

        time_label = Text("Time", font_size=32).next_to(x_axis, DOWN * 3)
        self.add(time_label)

        info_label = Text(f"{self.get_label()}: ", font_size=32)

        number = Integer(0)
        number.set_value(3)
        info_labels_group2 = VGroup(info_label, number) \
            .arrange(direction=RIGHT) \
            .move_to(pos(0, 5))
        self.add(info_labels_group2)

        self.camera.frame.move_to(np.array([5, 2, 0]))

        dot = Dot(point=pos(0, 0))
        self.wait()

        rate_limiter = self.get_rate_limiter()
        for x, count in enumerate([2, 1, 0, 4, 2, 3, 0, 2, 3, 1]):
            rate_limiter.tick(x)
            animations: List[Animation] = []
            for y in range(count):
                number.set_value(self.get_counter_label())

                should_allow = rate_limiter.check(CLIENT1)
                box = Box(x, y)
                box_color = GREEN if should_allow else RED
                box.set_stroke(box_color)
                box.set_fill(color=box_color, opacity=0.5)

                animations.append(FadeIn(box))

            animations.append(dot.animate.set_x(x + 1))
            if animations:
                self.play(*animations)
            else:
                self.wait(1)
        self.wait()


class FixWindowScene(RateLimitScene):

    def __init__(self):
        self.rate_limiter = FixedWindow()
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        pass

    def get_counter_label(self) -> int:
        return self.rate_limiter.counter[CLIENT1]


class TokenBucketScene(RateLimitScene):

    def __init__(self):
        self.rate_limiter = TokenBucketLimiter([CLIENT1])
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        pass

    def get_counter_label(self) -> int:
        return self.rate_limiter.tokens[CLIENT1]
