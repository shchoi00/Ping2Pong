from dataclasses import dataclass


@dataclass
class ShareData:
    def __init__(self):
        self.p1_x: int = 10
        self.p1_y: int = 200
        self.p2_x: int = 780
        self.p2_y: int = 200
        self.ball_x: int = 345
        self.ball_y: int = 195
        self.velo_x: int = 1
        self.velo_y: int = 1
        self.p1_score: int = 0
        self.p2_score: int = 0
        self.item_constructor: int = 1
        self.item_x: int = -999
        self.item_y: int = -999
        self.item_existence: bool = False
        self.last_hit: int = 0
        self.p1_item: bool = False
        self.p1_item_type: int = 0
        self.p2_item: bool = False
        self.p2_item_type: int = 0
        self.p1_paddle_height: int = 100
        self.p2_paddle_height: int = 100
        self.p1_item_time: list[int] = [0, 0, 0]
        self.p2_item_time: list[int] = [0, 0, 0]
        self.p1_item_used: list[bool] = [False, False, False]
        self.p2_item_used: list[bool] = [False, False, False]
        self.temp_velo_x: int = 0
        self.temp_velo_y: int = 0
        self.p1_ready: bool = False
        self.p2_ready: bool = False
        self.p1_start: bool = False
        self.p2_start: bool = False
