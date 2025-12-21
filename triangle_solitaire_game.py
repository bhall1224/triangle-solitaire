import pygame.event as event
import pygame.key as key
import pygame.mouse as mouse
from game_utils.game import Game
from pygame import Rect, Vector2
from pygame.locals import K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from triangle_solitaire import TriangleSolitaire
from triangle_solitaire_screen import TSSettings


class TriangleSolitaireGame(Game):
    def __init__(self, screen_settings: TSSettings, triangle_game: TriangleSolitaire):
        super().__init__(screen_settings)
        # seems silly, but ensures we're using the right instance
        self.screen_settings = screen_settings
        self.__carrying = False
        self.__dragging = False
        self.__mouse_radius: float = self.screen_settings.width / 40.0
        self.__mouse_pos: Vector2 = Vector2()
        self.__triangle_game = triangle_game

    def events(self, event: event.Event):
        if event.type == MOUSEBUTTONDOWN:
            self.__dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.__dragging = False

        if key.get_pressed()[K_ESCAPE]:
            self.running = False

    def __attempt_jump(self) -> bool:
        for i, point in enumerate(self.screen_settings.get_points()):
            if (
                not self.__triangle_game.has_marker(i)
                and self.__is_near_mouse(point)
                and self.__triangle_game.attempt_jump(i)
            ):
                return True

        return False

    def __is_near_mouse(self, point: Rect):
        return (self.__mouse_pos - point.center).magnitude() < self.__mouse_radius

    def update(self):
        if self.__dragging:
            self.__mouse_pos = Vector2(mouse.get_pos())
            self.screen_settings.carrying_marker(self.__mouse_pos, self.__carrying)
            if not self.__carrying:
                for i, point in enumerate(self.screen_settings.get_points()):
                    if self.__triangle_game.has_marker(i) and self.__is_near_mouse(
                        point
                    ):
                        self.__triangle_game.set_marker(i, False)
                        self.__carrying = True
                        self.selected_marker = i
                        self.__triangle_game.select_marker(i)
        elif self.__carrying:
            self.__carrying = False
            self.screen_settings.carrying_marker(carrying=self.__carrying)
            if not self.__attempt_jump():
                self.__triangle_game.set_marker(self.selected_marker, True)
            elif not self.__triangle_game.has_legal_moves():
                self.running = False
