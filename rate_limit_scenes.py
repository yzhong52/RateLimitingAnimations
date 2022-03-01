from abc import ABC
from manim import *

import numpy as np

from rate_limiters import RateLimiter, FixedWindow, TokenBucket, SlidingLog

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


x_axis_buffer = 1
x_axis_init_size = 10
request_counts = [2, 1, 0, 4, 2, 3, 0, 2, 3, 1]


def create_time_tick(x: int) -> [VMobject]:
    """
    Add a small vertical line on the time (x_axis) and a number lable
    """
    line = Line(pos(x, -0.1), pos(x, 0.1))
    text = Text(f"{x}", font_size=24).next_to(line, DOWN)
    return [line, text]


class RateLimitScene(MovingCameraScene):
    def __init__(self):
        super(RateLimitScene, self).__init__()
        self.label_offset_y = 0
        self.x_axis = Arrow(
            start=pos(-x_axis_buffer, 0),
            end=pos(x_axis_init_size + x_axis_buffer, 0),
            stroke_width=4
        )

        # A dot to indicate the current time
        self.time_dot = Dot(point=pos(0, 0))

    def get_rate_limiter(self) -> RateLimiter:
        pass

    def get_label(self) -> str:
        pass

    def get_counter_label(self) -> int:
        pass

    def set_up_scene(self):
        self.camera.frame.move_to(np.array([5, 2, 0]))

        x_axis = self.x_axis
        for x in range(0, 11):
            self.add(*create_time_tick(x))
        self.add(x_axis)

        time_label = Text("Time", font_size=32).next_to(x_axis, DOWN * 3)
        self.add(time_label)

        self.add(self.time_dot)

    def create_label_counter(self, label: str, label_color: str = WHITE, initial_value: int = 0) -> Integer:
        label = Text(f"{label}:", font_size=32, font="Comic Sans MS", color=label_color)
        counter = Integer(initial_value, color=label_color)
        group = VGroup(label, counter).arrange(direction=RIGHT)
        group.move_to(pos(0, 5 - self.label_offset_y), aligned_edge=LEFT)
        self.label_offset_y += 0.7
        self.add(group)
        return counter

    def construct(self):
        self.set_up_scene()

        counter = self.create_label_counter(self.get_label())
        allowed_count = self.create_label_counter("Allowed", label_color=GREEN)
        blocked_count = self.create_label_counter("Blocked", label_color=RED)

        self.wait()

        rate_limiter = self.get_rate_limiter()
        for current_time, count in enumerate(request_counts):
            rate_limiter.tick(current_time)
            animations: List[Animation] = [counter.animate.set_value(self.get_counter_label())]

            current_allowed_count = 0
            current_blocked_count = 0
            for y in range(count):
                allowed = rate_limiter.check(CLIENT1, current_time=current_time)
                if allowed:
                    current_allowed_count += 1
                else:
                    current_blocked_count += 1
                box = RequestBox(x=current_time, y=y, blocked=not allowed)
                animations.append(FadeIn(box))

            animations.append(
                allowed_count.animate.set_value(current_allowed_count)
            )
            animations.append(
                blocked_count.animate.set_value(current_blocked_count)
            )
            self.bring_to_front(self.time_dot)
            animations.append(self.time_dot.animate.set_x(current_time + 1))
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


class SlidingLogScene(RateLimitScene):

    def __init__(self):
        self.rate_limiter = SlidingLog()
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        return "Logs"

    def get_counter_label(self) -> int:
        return len(self.rate_limiter.logs[CLIENT1])


class TokenBucketScene(RateLimitScene):

    def __init__(self):
        self.rate_limiter = TokenBucket([CLIENT1])
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        return "Tokens"

    def get_counter_label(self) -> int:
        return self.rate_limiter.tokens[CLIENT1].count


class TokenBucketSceneProlonged(RateLimitScene):
    def __init__(self):
        self.rate_limiter = TokenBucket([CLIENT1])
        super().__init__()

    def get_rate_limiter(self) -> RateLimiter:
        return self.rate_limiter

    def get_label(self) -> str:
        return "Tokens"

    def get_counter_label(self) -> int:
        return self.rate_limiter.tokens[CLIENT1].count

    def construct(self):
        self.set_up_scene()

        rate_limiter = self.get_rate_limiter()

        current_tokens_counter = 0
        current_allowed_count = 0
        current_blocked_count = 0
        for current_time, count in enumerate(request_counts):
            rate_limiter.tick(current_time)
            current_tokens_counter = self.get_counter_label()

            current_allowed_count = 0
            current_blocked_count = 0
            for y in range(count):
                allowed = rate_limiter.check(CLIENT1, current_time=current_time)
                if allowed:
                    current_allowed_count += 1
                else:
                    current_blocked_count += 1
                box = RequestBox(x=current_time, y=y, blocked=not allowed)
                self.add(box)

        self.time_dot.set_x(len(request_counts))
        animations: List[Animation] = []

        tokens_count = self.create_label_counter(self.get_label(), initial_value=current_tokens_counter)
        allowed_count = self.create_label_counter("Allowed", label_color=GREEN, initial_value=current_allowed_count)

        # There seems to be a weird bug, without setting the initial value to '0' first, the number is not scaled
        # properly
        blocked_count = self.create_label_counter("Blocked", label_color=RED, initial_value=0)
        self.play(blocked_count.animate.set_value(current_blocked_count))

        camera: MovingCamera = self.camera

        camera_width_padding = camera.frame_width - len(request_counts)
        self.bring_to_front(self.time_dot)

        additional_requests = [0, 0, 1, 0, 0, 0, 5, 2, 1, 0, 0]
        for current_time_x, current_requests_count in enumerate(additional_requests):
            animations.clear()

            current_time_x += len(request_counts)
            next_time_x = current_time_x + 1

            self.rate_limiter.tick(current_time_x)
            animations.append(tokens_count.animate.set_value(self.get_counter_label()))

            animations.append(
                self.x_axis.animate.put_start_and_end_on(
                    start=pos(-x_axis_buffer, 0),
                    end=pos(next_time_x + x_axis_buffer, 0)
                )
            )
            animations.append(self.time_dot.animate.set_x(current_time_x))

            animations.extend([FadeIn(obj) for obj in create_time_tick(next_time_x)])

            current_allowed_count = 0
            current_blocked_count = 0
            for y in range(current_requests_count):
                allowed = rate_limiter.check(CLIENT1, current_time=current_time_x)
                if allowed:
                    current_allowed_count += 1
                else:
                    current_blocked_count += 1
                box = RequestBox(x=current_time_x, y=y, blocked=not allowed)
                animations.append(FadeIn(box))

            animations.append(
                allowed_count.animate.set_value(current_allowed_count)
            )
            animations.append(
                blocked_count.animate.set_value(current_blocked_count)
            )

            zoom_out_animation = camera.frame.animate \
                .move_to(np.array([next_time_x / 2, 2, 0])) \
                .set_width(camera_width_padding + next_time_x)

            animations.append(zoom_out_animation)
            self.play(*animations)
            self.bring_to_front(self.time_dot)

        self.wait()
