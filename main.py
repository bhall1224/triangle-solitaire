import json
import os

import pygame
from triangle_solitaire import TriangleSolitaire
from triangle_solitaire_game import TriangleSolitaireGame
from triangle_solitaire_screen import TSGameConfig, TSScreenReference

pygame.init()

def run_ts_game(config):
    board = config["board"]
    screen = config["screen"]
    screen_w = int(screen["width"])
    screen_h = screen_w / 16 * 9
    size = board["size"]
    game = TriangleSolitaire(size=size)
    settings = TSScreenReference(
        config=TSGameConfig(
            board=TSGameConfig.Board(
                size=board["size"],
                color=board["color"],
                background_color=board["background-color"],
                border_color=board["border-color"],
                placement_colors=board["placement-colors"],
            ),
            marker=TSGameConfig.Marker(
                color=config["marker"]["color"],
                selected_color=config["marker"]["selected-color"],
            ),
        ),
        width=screen_w,
        height=screen_h,
        bg_color=board["background-color"],
        game=game,
    )
    main = TriangleSolitaireGame(screen_ref=settings, triangle_game=game)
    main.run()

    print("game over")


if __name__ == "__main__":
    with open(
        os.path.join(os.path.dirname(__file__), ".config", "triangle_solitaire.json"),
        mode="r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)
        run_ts_game(config)
