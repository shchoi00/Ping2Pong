from dataclasses import dataclass


@dataclass
class Protocol:
    command: str = ""
    hit: bool = False  # ball이 paddle에 hit하면 True로 바뀜, 이때마다 ball 위치 동기화
    skill: bool = False  # skill 사용하면 True로 바뀜, ball 위치, 속도 동기화
    my_paddle_x: int = 0
    my_paddle_y: int = 0
    other_paddle_x: int = 0
    other_paddle_y: int = 0
    ball_x: int = 0
    ball_y: int = 0
    velo_x: int = 0
    velo_y: int = 0
    player: int = 0
    counter_player: int = 0
    game: int = 0
    pause: bool = False
