# -*- coding: utf-8 -*-
from random import choice, randint, uniform
from re import M
from socket import *
from threading import Thread
from threading import Lock
from xml.sax.handler import DTDHandler
from protocol import Protocol
import pickle
from queue import Queue
from pygame import time
from sharedata import ShareData


# 쓰레드간 공유할 변수 선언
shared_data: list[ShareData] = []


class ClientThread(Thread):
    num_connection: int = 0
    lock = Lock()

    def __init__(self, clientAddress, clientsocket):
        Thread.__init__(self)

        # 쓰레드 공유변수 초기화,
        # 이 변수를 사용하여 서버-클라이언트간 통신을 구현함.
        shared_data.append(ShareData())
        self.clientAddress = clientAddress
        self.clientsocket: socket = clientsocket

        self.clock = time.Clock()
        self.protocol = Protocol()
        self.message_count = 0
        self.player = ClientThread.num_connection
        if self.player % 2 == 1:
            self.counter_player = self.player + 1
        else:
            self.counter_player = self.player - 1

    def run(self):
        print("Connection from : ", self.clientAddress)
        while True:
            self.clock.tick(60)
            response_msg = self.Receive()

            if response_msg.command == "ConnChk":
                print(ClientThread.num_connection)
                self.CheckConnection()
            if response_msg.command == "SessChk":
                self.CheckSession(response_msg)
            if response_msg.command == "Update":
                self.Update(response_msg)
            if response_msg.command == "bye":
                print(response_msg.player)
                break

            print("shared  ", ClientThread.num_connection)

            self.Request()

        print("Client at ", self.clientAddress, " disconnected...")
        with ClientThread.lock:
            ClientThread.num_connection -= 1
        print(ClientThread.num_connection)

    def CheckConnection(self):
        self.protocol.command = "ConnChk"
        ClientThread.num_connection += 1
        self.protocol.player = ClientThread.num_connection
        print("num con", ClientThread.num_connection)

    def CheckSession(self, response_msg: Protocol):
        self.protocol.command = "SessChk"
        self.protocol.player = ClientThread.num_connection
        print("num con", ClientThread.num_connection)
        print("response_msg   ", response_msg)
        if response_msg.player % 2 == 1:  # 1P
            identifier: int = response_msg.player - 1
            shared_data[identifier].p1_ready = response_msg.my_ready
            shared_data[identifier].p1_start = response_msg.my_start
            self.protocol.other_ready = shared_data[identifier].p2_ready
        else:  # 2P
            identifier: int = response_msg.player - 2
            shared_data[identifier].p2_ready = response_msg.my_ready
            shared_data[identifier].p2_start = response_msg.my_start
            self.protocol.other_ready = shared_data[identifier].p1_ready
        shared_data[identifier].p1_score = 0
        shared_data[identifier].p2_score = 0
        if response_msg.message != "":
            shared_data[identifier].message.append(response_msg.message)
            shared_data[identifier].message_count += 1
        self.protocol.message = ""
        if shared_data[identifier].message_count != self.message_count:
            self.protocol.message = shared_data[identifier].message[shared_data[identifier]
                                                                    .message_count - 1]
            self.message_count += 1
        self.protocol.game_ready = shared_data[identifier].p1_ready and shared_data[identifier].p2_ready
        self.protocol.game_start = shared_data[identifier].p1_start and shared_data[identifier].p2_start

    def Update(self, response_msg: Protocol):
        print("UPDATE")
        ClientThread.lock.acquire()
        self.protocol.command = "Update"

        # 클라이언트의 키 입력을 처리하는 부분
        # identifier = 각 쓰레드간 다른 공유변수를 사용하도록 하는 식별자
        # 쓰레드 1,2의 식별자 값은 0,
        # 3과 4의 식별자 값은 2가 된다.

        # 홀수번째 플레이어일 경우 (좌측 막대 배정)
        if response_msg.player % 2 == 1:
            identifier: int = response_msg.player - 1
            if response_msg.pad_up == True:
                shared_data[identifier].p1_y -= 6.5*response_msg.dt
            elif response_msg.pad_dn == True:
                shared_data[identifier].p1_y += 6.5*response_msg.dt

            # 아이템 사용
            # 1번 아이템 = 막대 길이 증가
            # 2번 아이템 = 원하는 타이밍에 공 일시정지
            # 3번 아이템 = 꽝(임시, 보류중)
            if response_msg.item_use == True and not shared_data[identifier].p1_item_used[shared_data[identifier].p1_item_type-1]:
                shared_data[identifier].p1_item_used[shared_data[identifier].p1_item_type-1] = True
                shared_data[identifier].p1_item = False
                shared_data[identifier].p1_item_time[shared_data[identifier].p1_item_type-1] = 0
                if shared_data[identifier].p1_item_type == 2:
                    shared_data[identifier].tempvelo_x = shared_data[identifier].velo_x
                    shared_data[identifier].tempvelo_y = shared_data[identifier].velo_y
                    shared_data[identifier].velo_y = 0
                    shared_data[identifier].velo_x = 0
                shared_data[identifier].p1_item_type = 0
            # 아이템 종료
            if shared_data[identifier].p1_item_used[0]:
                if shared_data[identifier].p1_item_time[0] >= 10000:
                    if shared_data[identifier].p1_paddle_height > 100:
                        shared_data[identifier].p1_paddle_height -= 5
                    else:
                        shared_data[identifier].p1_paddle_height = 100
                        shared_data[identifier].p1_item_time[0] = 0
                        shared_data[identifier].p1_item_used[0] = False
                else:
                    if shared_data[identifier].p1_paddle_height < 300:
                        shared_data[identifier].p1_paddle_height += 5
                    else:
                        shared_data[identifier].p1_paddle_height = 300
            if shared_data[identifier].p1_item_used[1]:
                if shared_data[identifier].p1_item_time[1] >= 1500:
                    shared_data[identifier].p1_item_time[1] = 0
                    shared_data[identifier].p1_item_used[1] = False
                    shared_data[identifier].velo_x = shared_data[identifier].tempvelo_x * \
                        uniform(1.5, 2)
                    shared_data[identifier].velo_y = shared_data[identifier].tempvelo_y * \
                        choice([uniform(-2, -1.1), uniform(1.1, 2)])

            if shared_data[identifier].p1_y < 0:
                shared_data[identifier].p1_y = 0
            elif shared_data[identifier].p1_y + shared_data[identifier].p1_paddle_height > 600:
                shared_data[identifier].p1_y = 600 - \
                    shared_data[identifier].p1_paddle_height
            self.protocol.my_paddle_x = shared_data[identifier].p1_x
            self.protocol.my_paddle_y = shared_data[identifier].p1_y
            self.protocol.other_paddle_x = shared_data[identifier].p2_x
            self.protocol.other_paddle_y = shared_data[identifier].p2_y
            self.protocol.has_item = shared_data[identifier].p1_item
            self.protocol.other_has_item = shared_data[identifier].p2_item
            self.protocol.item_type = shared_data[identifier].p1_item_type
            self.protocol.my_paddle_height = shared_data[identifier].p1_paddle_height
            self.protocol.other_paddle_height = shared_data[identifier].p2_paddle_height

            # 아이템 지속시간 처리
            for i in range(3):
                if shared_data[identifier].p1_item_used[i]:
                    shared_data[identifier].p1_item_time[i] += self.clock.get_time()

            # 짝수번째 플레이어일 경우 (우측 막대 배정)
        else:
            identifier: int = response_msg.player - 2
            if response_msg.pad_up == True:
                shared_data[identifier].p2_y -= 6.5*response_msg.dt
            elif response_msg.pad_dn == True:
                shared_data[identifier].p2_y += 6.5*response_msg.dt
            if shared_data[identifier].p2_y < 0:
                shared_data[identifier].p2_y = 0
            elif shared_data[identifier].p2_y + shared_data[identifier].p2_paddle_height > 600:
                shared_data[identifier].p2_y = 600 - \
                    shared_data[identifier].p2_paddle_height
            self.protocol.my_paddle_x = shared_data[identifier].p2_x
            self.protocol.my_paddle_y = shared_data[identifier].p2_y
            self.protocol.other_paddle_x = shared_data[identifier].p1_x
            self.protocol.other_paddle_y = shared_data[identifier].p1_y
            self.protocol.has_item = shared_data[identifier].p2_item
            self.protocol.other_has_item = shared_data[identifier].p1_item
            self.protocol.item_type = shared_data[identifier].p2_item_type
            self.protocol.my_paddle_height = shared_data[identifier].p2_paddle_height
            self.protocol.other_paddle_height = shared_data[identifier].p1_paddle_height

            # 아이템 사용
            # 1번 아이템 = 막대 길이 증가
            # 2번 아이템 = 원하는 타이밍에 공 일시정지
            # 3번 아이템 = 꽝(임시, 보류중)
            if response_msg.item_use == True and not shared_data[identifier].p2_item_used[shared_data[identifier].p2_item_type-1]:
                shared_data[identifier].p2_item_used[shared_data[identifier].p2_item_type-1] = True
                shared_data[identifier].p2_item = False
                shared_data[identifier].p2_item_time[shared_data[identifier].p2_item_type-1] = 0
                if shared_data[identifier].p2_item_type == 2:
                    shared_data[identifier].tempvelo_x = shared_data[identifier].velo_x
                    shared_data[identifier].tempvelo_y = shared_data[identifier].velo_y
                    shared_data[identifier].velo_y = 0
                    shared_data[identifier].velo_x = 0
                shared_data[identifier].p2_item_type = 0
            # 아이템 종료
            if shared_data[identifier].p2_item_used[0]:
                if shared_data[identifier].p2_item_time[0] >= 10000:
                    if shared_data[identifier].p2_paddle_height > 100:
                        shared_data[identifier].p2_paddle_height -= 5
                    else:
                        shared_data[identifier].p2_paddle_height = 100
                        shared_data[identifier].p2_item_time[0] = 0
                        shared_data[identifier].p2_item_used[0] = False
                else:
                    if shared_data[identifier].p2_paddle_height < 300:
                        shared_data[identifier].p2_paddle_height += 5
                    else:
                        shared_data[identifier].p2_paddle_height = 300
            if shared_data[identifier].p2_item_used[1]:
                if shared_data[identifier].p2_item_time[1] >= 1500:
                    shared_data[identifier].p2_item_time[1] = 0
                    shared_data[identifier].p2_item_used[1] = False
                    shared_data[identifier].velo_x = shared_data[identifier].tempvelo_x * \
                        uniform(1.5, 2)
                    shared_data[identifier].velo_y = shared_data[identifier].tempvelo_y * \
                        choice([uniform(-2, -1.1), uniform(1.1, 2)])

            # 아이템 지속시간 처리
            for i in range(3):
                if shared_data[identifier].p2_item_used[i]:
                    shared_data[identifier].p2_item_time[i] += self.clock.get_time()

            # 공의 움직임
        shared_data[identifier].ball_x += shared_data[identifier].velo_x * \
            response_msg.dt
        shared_data[identifier].ball_y += shared_data[identifier].velo_y * \
            response_msg.dt

        # 승패 처리부분
        if shared_data[identifier].ball_x >= 790:
            shared_data[identifier].last_hit = 1
            shared_data[identifier].item_constructor += 100
            shared_data[identifier].p1_score += 1
            shared_data[identifier].ball_x = 400
            shared_data[identifier].ball_y = 300
            shared_data[identifier].velo_x = -1 * response_msg.dt
            shared_data[identifier].velo_y = -1 * response_msg.dt
            shared_data[identifier].item_constructor += shared_data[identifier].item_constructor * 2
        elif shared_data[identifier].ball_x <= 0:
            shared_data[identifier].last_hit = 2
            shared_data[identifier].item_constructor += 100
            shared_data[identifier].p2_score += 1
            shared_data[identifier].ball_x = 400
            shared_data[identifier].ball_y = 300
            shared_data[identifier].velo_x = 1 * response_msg.dt
            shared_data[identifier].velo_y = -1 * response_msg.dt
            shared_data[identifier].item_constructor += shared_data[identifier].item_constructor * 2

            # 공과 상단 또는 하단의 충돌 처리부분
        if shared_data[identifier].ball_y >= 590:
            if randint(1, 16384) <= shared_data[identifier].item_constructor and not shared_data[identifier].item_existence:
                shared_data[identifier].item_x = randint(250, 500)
                shared_data[identifier].item_y = randint(150, 400)
                shared_data[identifier].item_constructor = 0
                shared_data[identifier].item_existence = True
            else:
                shared_data[identifier].item_constructor += 10
            shared_data[identifier].velo_y = - shared_data[identifier].velo_y
        if shared_data[identifier].ball_y <= 0:
            if randint(1, 16384) <= shared_data[identifier].item_constructor and not shared_data[identifier].item_existence:
                shared_data[identifier].item_x = randint(250, 500)
                shared_data[identifier].item_y = randint(150, 400)
                shared_data[identifier].item_constructor = 0
                shared_data[identifier].item_existence = True
            else:
                shared_data[identifier].item_constructor += 10
            shared_data[identifier].velo_y = - shared_data[identifier].velo_y

            # 공과 막대의 충돌 처리부분
            # 좌측 플레이어 막대와 공 충돌
        if shared_data[identifier].ball_x < 20 and (shared_data[identifier].p1_y < shared_data[identifier].ball_y and shared_data[identifier].p1_y + shared_data[identifier].p1_paddle_height > shared_data[identifier].ball_y):
            if randint(1, 4096) <= shared_data[identifier].item_constructor and not shared_data[identifier].item_existence:
                shared_data[identifier].item_x = randint(250, 500)
                shared_data[identifier].item_y = randint(150, 400)
                shared_data[identifier].item_constructor = 0
                shared_data[identifier].item_existence = True
            else:
                shared_data[identifier].item_constructor += shared_data[identifier].item_constructor
            shared_data[identifier].velo_x = - shared_data[identifier].velo_x * \
                (response_msg.dt * uniform(0.6, 0.75))
            shared_data[identifier].last_hit = 1

            # 좌측 플레이어 끌어치기 구현용 코드
            if response_msg.player % 2 == 1:
                if response_msg.pad_up == True:
                    shared_data[identifier].velo_y = shared_data[identifier].velo_y + \
                        uniform(-1, -0.1) * response_msg.dt
                elif response_msg.pad_dn == True:
                    shared_data[identifier].velo_y = shared_data[identifier].velo_y + \
                        uniform(0.1, 1) * response_msg.dt
            else:
                shared_data[identifier].velo_y = shared_data[identifier].velo_y + \
                    uniform(-0.2, 0.2) * response_msg.dt

            # 우측 플레이어 막대와 공 충돌
        if shared_data[identifier].ball_x > 770 and (shared_data[identifier].p2_y < shared_data[identifier].ball_y and shared_data[identifier].p2_y + shared_data[identifier].p2_paddle_height > shared_data[identifier].ball_y):
            # 아이템 생성 조건 확인
            if randint(1, 4096) <= shared_data[identifier].item_constructor and not shared_data[identifier].item_existence:
                shared_data[identifier].item_x = randint(250, 500)
                shared_data[identifier].item_y = randint(150, 200)
                shared_data[identifier].item_constructor = 0
                shared_data[identifier].item_existence = True
            else:
                shared_data[identifier].item_constructor += shared_data[identifier].item_constructor
            shared_data[identifier].velo_x = - shared_data[identifier].velo_x * \
                (response_msg.dt * uniform(0.55, 0.65))
            shared_data[identifier].last_hit = 2

            # 우측 플레이어 끌어치기 구현용 코드
            if response_msg.player % 2 == 0:
                if response_msg.pad_up == True:
                    shared_data[identifier].velo_y = shared_data[identifier].velo_y + \
                        uniform(-1, -0.1) * response_msg.dt
                elif response_msg.pad_dn == True:
                    shared_data[identifier].velo_y = shared_data[identifier].velo_y + \
                        uniform(0.1, 1) * response_msg.dt
            else:
                shared_data[identifier].velo_y = shared_data[identifier].velo_y + \
                    uniform(-0.2, 0.2) * response_msg.dt

            # 아이템 획득처리
        if (shared_data[identifier].ball_x+10 > shared_data[identifier].item_x and shared_data[identifier].ball_x < shared_data[identifier].item_x+50) and (shared_data[identifier].item_y < shared_data[identifier].ball_y and shared_data[identifier].item_y + 50 > shared_data[identifier].ball_y):
            shared_data[identifier].item_x = -999
            shared_data[identifier].item_y = -999
            shared_data[identifier].item_existence = False
            shared_data[identifier].item_constructor = 0
            if shared_data[identifier].last_hit == 1:
                shared_data[identifier].p1_item = True
                shared_data[identifier].p1_item_type = randint(1, 3)
            elif shared_data[identifier].last_hit == 2:
                shared_data[identifier].p2_item = True
                shared_data[identifier].p2_item_type = randint(1, 3)
        # 서버에서 처리한 여러 데이터를 프로토콜에 저장하여 클라이언트에 전송
        self.protocol.ball_x = shared_data[identifier].ball_x
        self.protocol.ball_y = shared_data[identifier].ball_y
        self.protocol.score = [
            shared_data[identifier].p1_score, shared_data[identifier].p2_score]
        self.protocol.item_x = shared_data[identifier].item_x
        self.protocol.item_y = shared_data[identifier].item_y
        self.protocol.ball_shine = [
            shared_data[identifier].p1_item_used[1], shared_data[identifier].p2_item_used[1]]

        print("Other Paddle: ", self.protocol.other_paddle_x,
              self.protocol.other_paddle_y)
        print("Other Ball: ", self.protocol.ball_x,
              self.protocol.ball_y)

        print("request,  ", self.protocol.command)
        ClientThread.lock.release()

    def Request(self):
        ClientThread.lock.acquire()
        send_msg = pickle.dumps(self.protocol)
        self.clientsocket.sendall(send_msg)
        ClientThread.lock.release()

    def Receive(self) -> Protocol:
        shared_data = self.clientsocket.recv(4096)
        print(len(shared_data))
        response_msg: Protocol = pickle.loads(shared_data)
        print("Received: ", response_msg.command)
        print("from player: ", response_msg.player)
        return response_msg


serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8082))
serverSock.listen(1)

while True:
    serverSock.listen(2)
    clientsock, clientAddress = serverSock.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
