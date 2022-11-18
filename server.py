from re import M
from socket import *
from threading import Thread
from threading import Lock
from protocol import Protocol
import pickle
import json

# 쓰레드끼리 데이터를 공유하는 클래스


class Shared(object):
    current_shared = 0  # 현재 몇개의 클라이언트가 연결 되어 있는지
    player_data = []

    def __init__(self, hit, skill, my_paddle_x, my_paddle_y, other_paddle_x, other_paddle_y, ball_x, ball_y, velo_x, velo_y):
        self.hit = 0  # ball이 paddle에 hit하면 1로 바뀜, 이때마다 ball 위치 동기화
        self.skill = 0  # skill 사용하면 1로 바뀜, ball 위치, 속도 동기화
        self.my_paddle_x = 0
        self.my_paddle_y = 0
        self.other_paddle_x = 0
        self.other_paddle_y = 0
        self.ball_x = 0
        self.ball_y = 0
        self.velo_x = 0
        self.velo_y = 0

    def InitPlayerData(self):
        self.player_data.append(Shared(0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def PutMyPaddeld(self, player, x, y):
        self.player_data[player-1].my_paddle_x = x
        self.player_data[player-1].my_paddle_y = y

    def PutHit(self, player, hit):
        self.player_data[player-1].hit = hit

    def PutSkill(self, player, skill):
        self.player_data[player-1].skill = skill

    def PutMyPaddeld(self, player, x, y):
        self.player_data[player-1].my_paddle_x = x
        self.player_data[player-1].my_paddle_y = y

    def PutBall(self, player, x, y):
        self.player_data[player-1].ball_x = x
        self.player_data[player-1].ball_y = y

    def PutVelo(self, player, x, y):
        self.player_data[player-1].velo_x = x
        self.player_data[player-1].velo_y = y

    def GetHit(self, player):
        return self.player_data[player-1].hit

    def GetSkill(self, player):
        return self.player_data[player-1].skill

    def GetOtherPaddle(self, player):
        return self.player_data[player-1].other_paddle_x, self.player_data[player-1].other_paddle_y

    def GetBall(self, player):
        return self.player_data[player-1].ball_x, self.player_data[player-1].ball_y

    def GetVelo(self, player):
        return self.player_data[player-1].velo_x, self.player_data[player-1].velo_y

    def PrintData(self):
        for e in self.player_data:
            print(e)


class ClientThread(Thread):

    # lock = Lock()

    def __init__(self, clientAddress, clientsocket, lock, shared: Shared):
        Thread.__init__(self)
        super(ClientThread, self).__init__()

        self.clientAddress = clientAddress
        self.clientsocket = clientsocket
        self.request_msg = "initialized"
        self.lock = lock
        self.shared = shared
        self.protocol = Protocol()

        with self.lock:
            self.shared.current_shared += 1
        print("New connection added: ", clientAddress)

        self.player = self.shared.current_shared
        if self.player % 2 == 1:
            self.counter_player = self.player + 1
        else:
            self.counter_player = self.player - 1

    def run(self):
        print("Connection from : ", self.clientAddress)
        while True:
            response_msg = self.Receive()
            print("receive, ", response_msg)

            if response_msg.command == "ConnChk":
                print(self.shared.current_shared)
                self.CheckConnection()
            if response_msg.command == "SessChk":
                self.CheckSession()
            if response_msg.command == "Update":
                self.Update(response_msg)
            if response_msg.command == "bye":
                print(response_msg.player)
                self.shared.PrintData()
                break

            print("shared  ", self.shared.current_shared)

            # request_msg = "[REFLECT}"+response_msg

            # print("To client: ", self.request_msg)
            self.Request()

        print("Client at ", self.clientAddress, " disconnected...")
        with self.lock:
            self.shared.current_shared -= 1
        print(self.shared.current_shared)

    def CheckConnection(self):
        self.protocol.command = "ConnChk"

        self.protocol.player = self.shared.current_shared
        self.shared.PrintData()

    def CheckSession(self):
        self.protocol.command = "SessChk"
        self.protocol.player = self.shared.current_shared

    def Update(self, response_msg: Protocol):
        player = response_msg.player
        self.lock.acquire()
        self.shared.PutMyPaddeld(
            player, response_msg.my_paddle_x, response_msg.my_paddle_y)
        self.shared.PutBall(player, response_msg.ball_x, response_msg.ball_y)
        self.shared.PutVelo(player, response_msg.ball_x, response_msg.ball_y)
        self.shared.PutHit(player, response_msg.hit)
        self.shared.PutSkill(player, response_msg.skill)
        print(self.protocol.command)
        print(self.shared.player_data[player - 1])
        print("player:  ", response_msg.player,
              " counter ", response_msg.counter_player)
        print(self.protocol.other_paddle_x,
              self.protocol.other_paddle_y, response_msg.counter_player)
        self.protocol.other_paddle_x, self.protocol.other_paddle_y = self.shared.GetOtherPaddle(
            response_msg.counter_player)

        print("request,  ", self.protocol.command)
        self.Request()
        self.lock.release()

    def Request(self):
        self.lock.acquire()
        print("request,  ", self.protocol)
        send_msg = pickle.dumps(self.protocol)
        self.clientsocket.send(send_msg)
        self.lock.release()

    def Receive(self) -> Protocol:
        data = self.clientsocket.recv(4096)
        print(len(data))
        response_msg = pickle.loads(data)
        print("raw,  ", response_msg)
        return response_msg


serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8082))
serverSock.listen(1)

shared = Shared(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
lock = Lock()
while True:
    serverSock.listen(1)
    clientsock, clientAddress = serverSock.accept()
    newthread = ClientThread(clientAddress, clientsock, lock, shared)
    newthread.start()
