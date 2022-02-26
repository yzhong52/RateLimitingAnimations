from abc import ABC
from manim import *

import numpy as np

from rate_limiters import RateLimiter, FixedWindow, TokenBucketLimiter

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


class RequestBox(Box, ABC):
    """
    A class requesting a request. Red means that it is blocked, green means that it is allowed.
    """

    def __init__(self, x: int, y: int, blocked: bool):
        box_color = RED if blocked else GREEN
        super().__init__(x=x, y=y, color=box_color, stroke_color=box_color, fill_opacity=0.5)


class RateLimitScene(MovingCameraScene):
    def __init__(self):
        super(RateLimitScene, self).__init__()
        self.label_counts = 0

    def get_rate_limiter(self) -> RateLimiter:
        pass

    def get_label(self) -> str:
        pass

    def get_counter_label(self) -> int:
        pass

    def set_up_scene(self):
        self.camera.frame.move_to(np.array([5, 2, 0]))

        x_axis = Arrow(start=pos(-1, 0), end=pos(11, 0), stroke_width=4)
        for x in range(0, 11):
            line = Line(pos(x, -0.1), pos(x, 0.1))
            text = Text(f"{x}", font_size=24).next_to(line, DOWN)
            self.add(line, text)
        self.add(x_axis)

        time_label = Text("Time", font_size=32).next_to(x_axis, DOWN * 3)
        self.add(time_label)

    def create_label_counter(self, label: str, label_color: str = WHITE) -> Integer:
        label = Text(f"{label}:", font_size=32, font="Comic Sans MS", color=label_color)
        counter = Integer(0, color=label_color)
        group = VGroup(label, counter).arrange(direction=RIGHT).move_to(pos(0, 5 - self.label_counts))
        self.label_counts += .7
        self.add(group)
        return counter

    def construct(self):
        self.set_up_scene()

        counter = self.create_label_counter(self.get_label())
        allowed_count = self.create_label_counter("Allowed", label_color=GREEN)
        blocked_count = self.create_label_counter("Blocked", label_color=RED)

        dot = Dot(point=pos(0, 0))
        self.add(dot)

        self.wait()

        rate_limiter = self.get_rate_limiter()
        for x, count in enumerate([2, 1, 0, 4, 2, 3, 0, 2, 3, 1]):
            rate_limiter.tick(x)
            animations: List[Animation] = [counter.animate.set_value(self.get_counter_label())]

            current_allowed_count = 0
            current_blocked_count = 0
            for y in range(count):
                allowed = rate_limiter.check(CLIENT1)
                if allowed:
                    current_allowed_count += 1
                else:
                    current_blocked_count += 1
                box = RequestBox(x, y, not allowed)
                animations.append(FadeIn(box))

            animations.append(
                allowed_count.animate.set_value(current_allowed_count)
            )
            animations.append(
                blocked_count.animate.set_value(current_blocked_count)
            )
            animations.append(dot.animate.set_x(x + 1))
            self.play(*animations)
        self.wait()


class FixWindowScene(RateLimitScene):

    def __init__(self):
        self.rate_limiter = FixedWindow()
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        return "Counter"

    def get_counter_label(self) -> int:
        return self.rate_limiter.counter[CLIENT1]

    def set_up_scene(self):
        super().set_up_scene()
        for x in range(0, 15, 5):
            dashed_line = DashedLine(
                start=pos(x, -1),
                end=pos(x, 4),
                stroke_opacity=0.2,
                dash_length=0.1,
                dashed_ratio=0.5
            )
            self.add(dashed_line)


class TokenBucketScene(RateLimitScene):

    def __init__(self):
        self.rate_limiter = TokenBucketLimiter([CLIENT1])
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        return "Token"

    def get_counter_label(self) -> int:
        return self.rate_limiter.tokens[CLIENT1].count
