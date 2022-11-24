from dataclasses import dataclass


@dataclass
class Protocol:
    command: str = ""
    my_paddle_x: int = 0
    my_paddle_y: int = 0
    my_paddle_height: int = 0
    score = [0, 0]
    has_item: bool = False
    other_has_item: bool = False
    item_type: int = 0
    ball_shine = [False, False]
    item_use: bool = False
    pad_up: bool = False
    pad_dn: bool = False
    other_paddle_x: int = 0
    other_paddle_y: int = 0
    other_paddle_height: int = 0
    ball_x: int = 0
    ball_y: int = 0
    item_x: int = 0
    item_y: int = 0
    player: int = 0
    game: int = 0
    pause: bool = False
    dt: float = 0
