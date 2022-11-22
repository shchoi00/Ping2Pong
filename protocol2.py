from dataclasses import dataclass


@dataclass
class Protocol:
    command: str = ""
    skill: bool = False  # skill 사용하면 True로 바뀜, ball 위치, 속도 동기화
    my_paddle_x: int = 0
    my_paddle_y: int = 0
    score = [0,0]
    pad_up: bool = False
    pad_dn: bool = False
    other_paddle_x: int = 0
    other_paddle_y: int = 0
    ball_x: int = 0
    ball_y: int = 0
    item_x: int = 0
    item_y: int = 0
    player: int = 0
    counter_player: int = 0
    game: int = 0
    pause: bool = False
    dt: float = 0
