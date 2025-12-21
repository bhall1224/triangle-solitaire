import math
from dataclasses import dataclass

import pygame.draw as draw
from game_utils.screen import ScreenSettings
from pygame import Rect, Vector2
from triangle_solitaire import MAX_DEGREE, TriangleSolitaire

Coordinate = list[tuple[float, ...]]


@dataclass
class TSGameConfig:
    @dataclass
    class Board:
        size: int
        color: str
        background_color: str
        border_color: str
        placement_colors: list[str]

    @dataclass
    class Marker:
        color: str
        selected_color: str

    board: Board
    marker: Marker


class TSSettings(ScreenSettings):
    def __init__(
        self,
        config: TSGameConfig,
        game: TriangleSolitaire,
        *,
        width=0,
        height=0,
        frames_per_second=60,
        bg_color=None,
        bg_image=None,
    ):
        super().__init__(
            width=width,
            height=height,
            frames_per_second=frames_per_second,
            bg_color=bg_color,
            bg_image=bg_image,
        )
        self.__triangle_game = game

        # Configure triangles
        big_triangle_side = width / 2.0
        inscribed_hyp = big_triangle_side / 2.0
        start_x = big_triangle_side
        start_y = height / float(2**3)  # divide by 2 a bunch of times

        # fancy triangle stuff
        big_triangle_height = math.sqrt(big_triangle_side**2 - inscribed_hyp**2)

        # configure inner triangles
        inner_triangle_side = big_triangle_side / config.board.size

        # more fancy triangle stuff
        inner_triangle_height = math.sqrt(
            inner_triangle_side**2 - (inner_triangle_side / 2.0) ** 2
        )

        # set configurations
        self.__config = config
        self.__inner_triangle_color_codes = self.__config.board.placement_colors

        # verteces of the big triangle
        self.__board_corners = [
            (start_x, start_y),
            (start_x - inscribed_hyp, start_y + big_triangle_height),
            (start_x + inscribed_hyp, start_y + big_triangle_height),
        ]

        # big triangle border
        self.__border_weight = int(width * 0.005)

        # border verteces
        self.__border_corners = [
            (start_x, start_y - self.__border_weight),
            (
                start_x - inscribed_hyp - self.__border_weight,
                start_y + big_triangle_height + self.__border_weight / 2,
            ),
            (
                start_x + inscribed_hyp + self.__border_weight,
                start_y + big_triangle_height + self.__border_weight / 2,
            ),
        ]

        # generate inner triangle verteces
        # bottom right corner of triangle, inside border
        starting_point = self.__board_corners[1]
        self.__inner_triangle_points: list[Coordinate] = []

        for i in range(self.__config.board.size):
            start_x, start_y = starting_point
            for j in range(self.__config.board.size - i):
                # add points for inner triangle
                self.__inner_triangle_points.append(
                    [
                        (start_x + inner_triangle_side * j, start_y),
                        (
                            start_x + inner_triangle_side + inner_triangle_side * j,
                            start_y,
                        ),
                        (
                            start_x
                            + (inner_triangle_side / 2.0)
                            + inner_triangle_side * j,
                            start_y - inner_triangle_height,
                        ),
                    ]
                )

            starting_point = (
                start_x + (inner_triangle_side / 2.0),
                start_y - inner_triangle_height,
            )

        # configure markers
        self.__marker_size = inner_triangle_side / 6

        # n = sum of l ints
        self.__marker_positions = [
            Rect(0, 0, 0, 0)
            for _ in range(
                # l(l+1)/2
                int(self.__config.board.size * (self.__config.board.size + 1) / 2)
            )
        ]

        self.__carrying = False
        self.__mouse_pos = Vector2()

    def get_board_size(self) -> int:
        """
        The number of triangles along one side of the board
        """
        return self.__config.board.size

    def get_points(self):
        return self.__marker_positions

    def draw_marker(self, center: tuple[int, int] | Vector2, color: str | None = None):
        draw.circle(
            surface=self.screen,
            color=color or self.__config.marker.color,
            center=center,
            radius=self.__marker_size,
        )

    def draw_board(self):
        self.screen.fill(self.bg_color or "black")
        # draw background triangle
        draw.polygon(
            surface=self.screen,
            color=self.__config.board.color,
            points=self.__board_corners,
        )

        # draw outline of board
        draw.polygon(
            surface=self.screen,
            color=self.__config.board.border_color,
            points=self.__border_corners,
            width=self.__border_weight,
        )

        # draw inner triangles and markers
        for i, point in enumerate(self.__inner_triangle_points):
            self.__marker_positions[i] = draw.polygon(
                surface=self.screen,
                color=self.__inner_triangle_color_codes[
                    self.__triangle_game.get_nim_value(i) - 1
                ],
                points=point,
            )

            self.draw_marker(
                center=self.__marker_positions[i].center,
                color=self.__get_marker_color(i),
            )

    def carrying_marker(self, mouse_pos: Vector2 | None = None, carrying: bool = False):
        self.__carrying = carrying
        self.__mouse_pos = mouse_pos

    def update_screen(self):
        self.draw_board()

        if self.__carrying:
            self.draw_marker(self.__mouse_pos)

    def __get_marker_color(self, marker_id: int):
        if (
            self.__triangle_game.get_selected_marker() == marker_id
            and self.__triangle_game.has_marker(marker_id)
        ):
            return self.__config.marker.selected_color
        elif self.__triangle_game.has_marker(marker_id):
            return self.__config.marker.color
        else:
            return "black"
