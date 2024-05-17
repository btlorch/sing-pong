import pygame as pg


class Paddle:
    def __init__(self, name, x, y, width, height, speed, color=(255, 255, 255)):
        self.name = name
        self.surface = pg.Surface([width, height])
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color
        self.surface.fill(self.color)
        self.speed = speed
        self.desired_y = y
        self.movement_multiplier = 10

    def _move(self, x, y, time_delta):
        # self.rect[0] += int(x *  time_delta)
        # self.rect[1] += int(y *  time_delta)
        self.rect[0] += x * self.speed * time_delta
        self.rect[1] += y * self.speed * time_delta

    def move_up(self, time_delta):
        self.desired_y += (-1 * self.movement_multiplier)

    def move_down(self, time_delta):
        self.desired_y += (1 * self.movement_multiplier)

    def update_desired_y(self, desired_y):
        self.desired_y = desired_y

    def update_pos(self, time_delta):
        delta = self.desired_y - self.rect[1]

        # if self.name == "right":
        #     print(f"desired y: {self.desired_y}, self.rect[1]: {self.rect[1]}, delta: {delta}")

        if abs(delta) <= 3:
            return

        distance = 4
        direction = distance if delta >= 0 else -1 * distance
        self._move(0, direction, time_delta)

    def update(self, screen_rect):
        self.rect.clamp_ip(screen_rect)

    def render(self, screen):
        screen.blit(self.surface, self.rect)
