from protocol import Protocol
from socket import *
import pickle


class Network():
    def __init__(self):
        self.ip_addr = "127.0.0.1"
        self.port = 8082

        self.clientSock = socket(AF_INET, SOCK_STREAM)
        self.clientSock.connect((self.ip_addr, self.port))
        self.player = 0  # 내가 몇번째 플레이어 인지 저장
        self.counter_player = 0  # 상대가 몇번째 플레이어 인지 저장
        self.match = False  # 상대방이 연결됐는지 확인
        self.Connetion_establish = 0  # 내가 서버랑 연결 됐는지 저장
        self.protocol = Protocol()

    # Protocol 형식으로 서버에 보냄
    def Request(self):
        print(self.protocol.command)
        send_msg = pickle.dumps(self.protocol)
        self.clientSock.send(send_msg)

    # Protocol 형식으로 서버에게 받음
    def Receive(self) -> Protocol:
        data = self.clientSock.recv(4096)
        response_msg = pickle.loads(data)
        print("raw,  ", response_msg)
        return response_msg  # Protocol 형식으로 반환

    # 서버와 연결 후 자기가 몇번째 플레어이언지 확인
    def CheckConnetion(self):
        self.protocol.command = "ConnChk"
        print("Command 1  ", self.protocol.command)
        self.Request()
        response_msg = self.Receive()
        print("receive return")
        print("Command: ", response_msg.command)
        print("Game: ", response_msg.game)
        if response_msg.command == "ConnChk":
            self.Connetion_establish += 1

            self.player = response_msg.player
            self.game = int((int(self.player)+1) / 2)
        print("chkconn  ", self.Connetion_establish)

    # 서버에 다른 클라이언트가 연결 되었는지 확인,
    # 되었으면 게임 시작
    def CheckSession(self):
        self.protocol.command = "SessChk"
        self.Request()
        response_msg = self.Receive()

        print(response_msg.player)
        if response_msg.command == "SessChk":
            if int(response_msg.player) % 2 == 0:
                self.match = True
                return True
        return False

    def Update(self):
        self.protocol.command = "Update"
        print("Command  ", self.protocol.command)
        self.Request()
        print("MY X Y,  ", self.protocol.my_paddle_x, self.protocol.my_paddle_y)
        return self.Receive()

    def DisconnectSession(self):
        self.protocol.command = "bye"
        self.Request()
