import random
import typing
import pygame as pg
from .. import ball as ball_
from .. import paddle
from .. import tools
from .. import AI
from .. import audio_input

WINNING_SCORE = 9


class Classic(tools.States):
    def __init__(self, screen_rect, difficulty):
        tools.States.__init__(self)
        self.screen_rect = screen_rect
        self.score_text, self.score_rect = self.make_text(
            "SCOREBOARD_PLACEHOLDER", (255, 255, 255),
            (screen_rect.centerx, 100), 50)
        self.pause_text, self.pause_rect = self.make_text(
            "PAUSED", (255, 255, 255), screen_rect.center, 50)

        self.cover = pg.Surface((screen_rect.width, screen_rect.height))
        self.cover.fill(0)
        self.cover.set_alpha(200)

        #game specific content
        self.bg_color = (0, 0, 0)
        self.pause = False
        self.score = [0, 0]

        paddle_width = 10
        paddle_height = 100
        paddle_y = self.screen_rect.centery - (paddle_height // 2)
        paddle_speed = 200
        padding = 25  # padding from wall
        pad_right = screen_rect.width - paddle_width - padding

        self.ball = ball_.Ball(self.screen_rect, 10, 10, (0, 255, 0))
        self.paddle_left = paddle.Paddle(padding, paddle_y, paddle_width,
                                         paddle_height, paddle_speed / 1.5,
                                         (150, 150, 150))
        self.paddle_right = paddle.Paddle(pad_right, paddle_y, paddle_width,
                                          paddle_height, paddle_speed,
                                          (150, 150, 150))

        self.ai = AI.AIPaddle(self.screen_rect, self.ball.rect, difficulty)

        self.paddle_right.update_desired_y((screen_rect.bottom - screen_rect.top) / 2)
        audio_input.initialize_child_process(min_confidence_arg=0.2)

    def reset(self):
        self.pause = False
        self.score = [0, 0]
        self.ball.set_ball()

    def get_event(self, event, keys):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == self.controller_dict['back']:
                #self.button_sound.sound.play()
                self.done = True
                self.next = 'MENU'
                self.reset()
            elif event.key == self.controller_dict['pause']:
                self.pause = not self.pause
        elif event.type == self.background_music.track_end:
            self.background_music.track = (
                self.background_music.track + 1
            ) % len(self.background_music.tracks)
            pg.mixer.music.load(
                self.background_music.tracks[self.background_music.track])
            pg.mixer.music.play()

    def movement(self, keys, time_delta) -> bool:
        if self.ai.move_up:
            self.paddle_left.move_up(time_delta)
        if self.ai.move_down:
            self.paddle_left.move_down(time_delta)

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.paddle_right.move_up(time_delta)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.paddle_right.move_down(time_delta)

    def update(self, time_delta, keys):
        global WINNING_SCORE
        if not self.pause:
            self.ai.update(self.ball.rect, self.ball, self.paddle_left.rect)
            self.score_text, self.score_rect = self.make_text(
                '{}:{}'.format(self.score[0], self.score[1]), (255, 255, 255),
                (self.screen_rect.centerx, 25), 50)

            # Keep the paddles inside the screen
            self.paddle_left.update(self.screen_rect)
            self.paddle_right.update(self.screen_rect)

            hit_side = self.ball.update(self.paddle_left.rect,
                                        self.paddle_right.rect)

            if hit_side:
                self.adjust_score(hit_side)
                for i in range(0, len(self.score)):
                    if self.score[i] >= WINNING_SCORE:
                        pass

            # Process audio input
            # Top is 0, bottom grows larger. Invert the incoming pitch
            norm_pitch = audio_input.get_normalized_position()
            if norm_pitch and norm_pitch > 0:
                max_p = self.screen_rect.bottom
                abs_pos = (1.0 - norm_pitch) * max_p
                self.paddle_right.update_desired_y(abs_pos)

            self.movement(keys, time_delta)
            self.paddle_right.update_pos(time_delta)
            self.paddle_left.update_pos(time_delta)

        else:
            self.pause_text, self.pause_rect = self.make_text(
                "PAUSED", (255, 255, 255), self.screen_rect.center, 50)
        pg.mouse.set_visible(False)
        self.ai.reset()

    def render(self, screen):
        screen.fill(self.bg_color)
        screen.blit(self.score_text, self.score_rect)
        self.ball.render(screen)
        self.paddle_left.render(screen)
        self.paddle_right.render(screen)
        if self.pause:
            screen.blit(self.cover, (0, 0))
            screen.blit(self.pause_text, self.pause_rect)

    def adjust_score(self, hit_side):
        if hit_side == -1:
            self.score[1] += 1
        elif hit_side == 1:
            self.score[0] += 1

    def cleanup(self):
        pg.mixer.music.stop()
        self.background_music.setup(self.background_music_volume)
        audio_input.cleanup()

    def entry(self):
        pg.mixer.music.play()
