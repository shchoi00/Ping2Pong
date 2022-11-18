from dataclasses import dataclass


@dataclass
class Protocol:
    command = ""
    hit = 0  # ball이 paddle에 hit하면 1로 바뀜, 이때마다 ball 위치 동기화
    skill = 0  # skill 사용하면 1로 바뀜, ball 위치, 속도 동기화
    my_paddle_x = 0
    my_paddle_y = 0
    other_paddle_x = 0
    other_paddle_y = 0
    ball_x = 0
    ball_y = 0
    velo_x = 0
    velo_y = 0
    player = 0
    counter_player = 0
    game = 0
